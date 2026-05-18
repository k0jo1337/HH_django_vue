from django.contrib import admin

from .models import NewsPost


@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "is_published", "created_at", "updated_at")
    list_filter = ("is_published", "created_at")
    search_fields = ("title", "summary", "content")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Основное", {
            "fields": ("title", "summary", "content", "image", "is_published")
        }),
        ("Системная информация", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
