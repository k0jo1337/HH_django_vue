import json
import logging
import mimetypes
import random
import urllib.error
import urllib.parse
import urllib.request
import uuid

from django.conf import settings

logger = logging.getLogger(__name__)

VK_API_METHOD_URL = "https://api.vk.com/method/{}"
VK_MESSAGES_SEND_URL = VK_API_METHOD_URL.format("messages.send")
VK_MESSAGE_LIMIT = 4096


class VKNotificationError(Exception):
    pass


def _truncate_message(message):
    if len(message) <= VK_MESSAGE_LIMIT:
        return message

    return f"{message[: VK_MESSAGE_LIMIT - 3]}..."


def _join_url(base_url, path):
    if not base_url or not path:
        return None

    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def _raise_for_vk_error(payload):
    if "error" not in payload:
        return

    error = payload["error"]
    code = error.get("error_code", "unknown")
    error_message = error.get("error_msg", "Unknown VK API error")
    raise VKNotificationError(f"VK API error {code}: {error_message}")


def _read_json_response(request):
    try:
        with urllib.request.urlopen(
            request,
            timeout=settings.VK_NEWS_SEND_TIMEOUT,
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise VKNotificationError("VK API request failed") from exc

    _raise_for_vk_error(payload)
    return payload


def _vk_api_request(method, params):
    data = urllib.parse.urlencode(
        {
            **params,
            "access_token": settings.VK_BOT_TOKEN,
            "v": settings.VK_API_VERSION,
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        VK_API_METHOD_URL.format(method),
        data=data,
        method="POST",
    )
    return _read_json_response(request).get("response")


def _encode_multipart_formdata(field_name, file_path):
    boundary = uuid.uuid4().hex
    filename = file_path.rsplit("\\", 1)[-1].rsplit("/", 1)[-1]
    content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"

    with open(file_path, "rb") as file:
        file_data = file.read()

    body = b"\r\n".join(
        [
            f"--{boundary}".encode("utf-8"),
            (
                f'Content-Disposition: form-data; name="{field_name}"; '
                f'filename="{filename}"'
            ).encode("utf-8"),
            f"Content-Type: {content_type}".encode("utf-8"),
            b"",
            file_data,
            f"--{boundary}--".encode("utf-8"),
            b"",
        ]
    )
    headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
    return body, headers


def _upload_file(upload_url, field_name, file_path):
    body, headers = _encode_multipart_formdata(field_name, file_path)
    request = urllib.request.Request(upload_url, data=body, headers=headers, method="POST")
    return _read_json_response(request)


def _build_photo_attachment(saved_photo):
    attachment = f"photo{saved_photo['owner_id']}_{saved_photo['id']}"
    access_key = saved_photo.get("access_key")
    if access_key:
        attachment = f"{attachment}_{access_key}"
    return attachment


def upload_news_photo_to_vk(post):
    if not post.image:
        return None

    try:
        image_path = post.image.path
    except (NotImplementedError, ValueError):
        logger.warning("News post %s image has no local path for VK upload.", post.pk)
        return None

    upload_server = _vk_api_request(
        "photos.getMessagesUploadServer",
        {"peer_id": settings.VK_NEWS_PEER_ID},
    )
    upload_url = upload_server.get("upload_url")
    if not upload_url:
        raise VKNotificationError("VK photo upload server URL is missing")

    uploaded_photo = _upload_file(upload_url, "photo", image_path)
    saved_photos = _vk_api_request(
        "photos.saveMessagesPhoto",
        {
            "photo": uploaded_photo["photo"],
            "server": uploaded_photo["server"],
            "hash": uploaded_photo["hash"],
        },
    )

    if not saved_photos:
        raise VKNotificationError("VK photo save response is empty")

    return _build_photo_attachment(saved_photos[0])


def build_news_message(post, include_image_link=False):
    lines = [
        str(settings.VK_NEWS_MESSAGE_PREFIX).strip() or "Новая новость",
        "",
        post.title,
        post.summary,
    ]

    if post.content:
        lines.extend(["", post.content])

    if include_image_link and post.image:
        image_url = _join_url(settings.BACKEND_PUBLIC_URL, post.image.url)
        if image_url:
            lines.extend(["", f"Изображение: {image_url}"])

    if settings.NEWS_PUBLIC_URL:
        lines.extend(["", f"Читать на сайте: {settings.NEWS_PUBLIC_URL}"])

    message = "\n".join(line for line in lines if line is not None).strip()
    return _truncate_message(message)


def send_vk_message(message, attachment=None):
    if not settings.VK_NEWS_BOT_ENABLED:
        logger.debug("VK news bot is disabled.")
        return None

    if not settings.VK_BOT_TOKEN or not settings.VK_NEWS_PEER_ID:
        logger.warning("VK news bot is enabled, but token or peer_id is missing.")
        return None

    params = {
        "access_token": settings.VK_BOT_TOKEN,
        "v": settings.VK_API_VERSION,
        "peer_id": settings.VK_NEWS_PEER_ID,
        "random_id": random.randint(1, 2_147_483_647),
        "message": message,
    }
    if attachment:
        params["attachment"] = attachment

    data = urllib.parse.urlencode(params).encode("utf-8")
    request = urllib.request.Request(VK_MESSAGES_SEND_URL, data=data, method="POST")
    return _read_json_response(request).get("response")


def send_news_to_vk(post):
    attachment = None

    if post.image:
        try:
            attachment = upload_news_photo_to_vk(post)
        except Exception:
            logger.exception("Failed to upload news post %s image to VK.", post.pk)

    return send_vk_message(
        build_news_message(post),
        attachment=attachment,
    )
