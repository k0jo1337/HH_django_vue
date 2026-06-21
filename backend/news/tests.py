from unittest.mock import patch

from django.test import SimpleTestCase, TestCase, override_settings

from news.models import NewsPost
from news.services import build_news_message, send_vk_message


class VKNewsServiceTests(SimpleTestCase):
    @override_settings(
        VK_NEWS_MESSAGE_PREFIX="News",
        BACKEND_PUBLIC_URL="https://example.test",
        NEWS_PUBLIC_URL="https://example.test/home",
    )
    def test_build_news_message_contains_news_fields_without_image_link(self):
        post = NewsPost(
            title="Title",
            summary="Summary",
            content="Full content",
            image="news/example.jpg",
        )

        message = build_news_message(post)

        self.assertIn("News", message)
        self.assertIn("Title", message)
        self.assertIn("Summary", message)
        self.assertIn("Full content", message)
        self.assertNotIn("https://example.test/media/news/example.jpg", message)
        self.assertIn("https://example.test/home", message)

    @override_settings(
        VK_NEWS_MESSAGE_PREFIX="News",
        BACKEND_PUBLIC_URL="https://example.test",
        NEWS_PUBLIC_URL="https://example.test/home",
    )
    def test_build_news_message_can_include_image_link_as_fallback(self):
        post = NewsPost(
            title="Title",
            summary="Summary",
            image="news/example.jpg",
        )

        message = build_news_message(post, include_image_link=True)

        self.assertIn("https://example.test/media/news/example.jpg", message)

    @override_settings(VK_NEWS_BOT_ENABLED=False)
    def test_send_vk_message_returns_none_when_disabled(self):
        self.assertIsNone(send_vk_message("hello"))

    @override_settings(
        VK_NEWS_BOT_ENABLED=True,
        VK_BOT_TOKEN="token",
        VK_NEWS_PEER_ID="2000000001",
        VK_API_VERSION="5.199",
    )
    @patch("news.services._read_json_response")
    @patch("news.services.random.randint", return_value=123)
    def test_send_vk_message_includes_attachment(self, random_int, read_json_response):
        read_json_response.return_value = {"response": 1}

        response = send_vk_message("hello", attachment="photo1_2_key")

        self.assertEqual(response, 1)
        request = read_json_response.call_args.args[0]
        body = request.data.decode("utf-8")
        self.assertIn("attachment=photo1_2_key", body)


class VKNewsSignalTests(TestCase):
    @override_settings(VK_NEWS_BOT_ENABLED=True, VK_BOT_TOKEN="token", VK_NEWS_PEER_ID="2000000001")
    @patch("news.signals.send_news_to_vk")
    def test_created_published_news_is_sent_after_commit(self, send_news_to_vk):
        with self.captureOnCommitCallbacks(execute=True):
            post = NewsPost.objects.create(title="Title", summary="Summary")

        send_news_to_vk.assert_called_once_with(post)

    @override_settings(VK_NEWS_BOT_ENABLED=True, VK_BOT_TOKEN="token", VK_NEWS_PEER_ID="2000000001")
    @patch("news.signals.send_news_to_vk")
    def test_created_unpublished_news_is_not_sent(self, send_news_to_vk):
        NewsPost.objects.create(title="Title", summary="Summary", is_published=False)

        send_news_to_vk.assert_not_called()
