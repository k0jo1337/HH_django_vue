import logging

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import NewsPost
from .services import send_news_to_vk

logger = logging.getLogger(__name__)


def _send_created_news(news_id):
    post = NewsPost.objects.filter(pk=news_id, is_published=True).first()
    if not post:
        return

    try:
        send_news_to_vk(post)
    except Exception:
        logger.exception("Failed to send news post %s to VK.", news_id)


@receiver(post_save, sender=NewsPost)
def send_created_news_to_vk(sender, instance, created, **kwargs):
    if not created or not instance.is_published:
        return

    transaction.on_commit(lambda: _send_created_news(instance.pk))
