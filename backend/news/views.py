from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import NewsPost


def is_employee_user(user):
    return user.groups.filter(name="Сотрудник").exists()


def employee_forbidden_response():
    return Response(
        {"error": "Доступ запрещен. Требуются права сотрудника."},
        status=status.HTTP_403_FORBIDDEN,
    )


def get_news_payload_errors(title, summary):
    errors = {}
    if not title:
        errors["title"] = "Укажите заголовок новости."
    if not summary:
        errors["summary"] = "Укажите краткое описание новости."
    return errors


def serialize_news_post(post, request):
    image_url = None
    if post.image:
        image_url = request.build_absolute_uri(post.image.url)

    return {
        "id": post.id,
        "title": post.title,
        "summary": post.summary,
        "content": post.content,
        "image": image_url,
        "created_at": post.created_at.isoformat(),
        "updated_at": post.updated_at.isoformat(),
    }


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def list_news(request):
    if request.method == "POST":
        if not is_employee_user(request.user):
            return employee_forbidden_response()

        title = str(request.data.get("title", "")).strip()
        summary = str(request.data.get("summary", "")).strip()
        content = str(request.data.get("content", "")).strip()
        image = request.FILES.get("image")

        errors = get_news_payload_errors(title, summary)
        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        post = NewsPost.objects.create(
            title=title,
            summary=summary,
            content=content,
            image=image,
        )

        return Response(
            {"news": serialize_news_post(post, request)},
            status=status.HTTP_201_CREATED,
        )

    query = str(request.query_params.get("search", "")).strip()
    posts = NewsPost.objects.filter(is_published=True)

    if query:
        posts = posts.filter(
            Q(title__icontains=query)
            | Q(summary__icontains=query)
            | Q(content__icontains=query)
        )

    return Response({
        "news": [serialize_news_post(post, request) for post in posts],
    })


@api_view(["PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def news_detail(request, news_id):
    if not is_employee_user(request.user):
        return employee_forbidden_response()

    post = get_object_or_404(NewsPost, pk=news_id)

    if request.method == "DELETE":
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    title = str(request.data.get("title", "")).strip()
    summary = str(request.data.get("summary", "")).strip()
    content = str(request.data.get("content", "")).strip()
    image = request.FILES.get("image")

    errors = get_news_payload_errors(title, summary)
    if errors:
        return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

    post.title = title
    post.summary = summary
    post.content = content
    if image:
        post.image = image
    post.save()

    return Response({"news": serialize_news_post(post, request)})
