from django.contrib import admin
from django.utils.html import format_html
from .models import NewsPost


@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "is_published", "image_preview", "created_at", "updated_at")
    list_filter = ("is_published", "created_at")
    search_fields = ("title", "summary", "content")
    readonly_fields = ("created_at", "updated_at", "image_preview")

    fieldsets = (
        ("Основное", {
            "fields": ("title", "summary", "content", "image", "image_preview", "is_published")
        }),
        ("Системная информация", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def image_preview(self, obj):
        if obj.image and obj.image.url:
            return format_html('<img src="{}" style="max-width: 150px; max-height: 150px; border-radius: 8px;" />',
                               obj.image.url)
        return 'Нет изображения'

    image_preview.short_description = 'Превью изображения'

    actions = ['publish_news', 'unpublish_news']

    def publish_news(self, request, queryset):
        queryset.update(is_published=True)
        self.message_user(request, f'Новости опубликованы')

    publish_news.short_description = 'Опубликовать выбранные новости'

    def unpublish_news(self, request, queryset):
        queryset.update(is_published=False)
        self.message_user(request, f'Новости сняты с публикации')

    unpublish_news.short_description = 'Снять с публикации'