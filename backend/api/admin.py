from django.contrib import admin
from .models import Appeal


@admin.register(Appeal)
class AppealAdmin(admin.ModelAdmin):
    list_display = ("subject", "user", "specialist", "status", "created_at")
    list_filter = ("status", "specialist", "created_at")
    search_fields = ("subject", "message", "user__username", "user__email")
    readonly_fields = ("created_at", "updated_at")
