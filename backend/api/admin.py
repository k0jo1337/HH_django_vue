from django.contrib import admin
from .models import Appeal


@admin.register(Appeal)
class AppealAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_full_name', 'get_phone', 'get_email',
                    'get_hostel', 'get_room_number', 'subject', 'specialist',
                    'status', 'created_at')

    list_filter = ('status', 'specialist', 'created_at')

    search_fields = ('subject', 'message', 'user__username', 'user__email',
                     'user__first_name', 'user__last_name', 'user__profile__phone',
                     'user__profile__room_number', 'user__profile__hostel')

    readonly_fields = ('created_at', 'updated_at', 'get_full_name_display',
                       'get_phone_display', 'get_email_display', 'get_hostel_display',
                       'get_room_number_display')

    fieldsets = (
        ('Информация об отправителе', {
            'fields': ('user', 'get_full_name_display', 'get_phone_display',
                       'get_email_display', 'get_hostel_display', 'get_room_number_display')
        }),
        ('Обращение', {
            'fields': ('subject', 'specialist', 'message', 'status')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_full_name(self, obj):
        """ФИО для списка"""
        if obj.user:
            profile = getattr(obj.user, 'profile', None)
            middle_name = profile.middle_name if profile and not profile.has_no_middle_name else ''
            return f"{obj.user.last_name} {obj.user.first_name} {middle_name}".strip()
        return obj.user.username if obj.user else '-'
    get_full_name.short_description = 'ФИО отправителя'
    get_full_name.admin_order_field = 'user__last_name'

    def get_full_name_display(self, obj):
        """ФИО для формы"""
        if obj.user:
            profile = getattr(obj.user, 'profile', None)
            middle_name = profile.middle_name if profile and not profile.has_no_middle_name else ''
            return f"{obj.user.last_name} {obj.user.first_name} {middle_name}".strip()
        return obj.user.username if obj.user else '-'
    get_full_name_display.short_description = 'ФИО'

    def get_phone(self, obj):
        if obj.user and hasattr(obj.user, 'profile'):
            return obj.user.profile.phone or '-'
        return '-'
    get_phone.short_description = 'Телефон'

    def get_phone_display(self, obj):
        if obj.user and hasattr(obj.user, 'profile'):
            return obj.user.profile.phone or '-'
        return '-'
    get_phone_display.short_description = 'Телефон'

    def get_email(self, obj):
        if obj.user:
            return obj.user.email
        return '-'
    get_email.short_description = 'Email'

    def get_email_display(self, obj):
        if obj.user:
            return obj.user.email
        return '-'
    get_email_display.short_description = 'Email'

    def get_hostel(self, obj):
        if obj.user and hasattr(obj.user, 'profile'):
            return obj.user.profile.hostel or '-'
        return '-'
    get_hostel.short_description = 'Общежитие'

    def get_hostel_display(self, obj):
        if obj.user and hasattr(obj.user, 'profile'):
            return obj.user.profile.hostel or '-'
        return '-'
    get_hostel_display.short_description = 'Общежитие'

    def get_room_number(self, obj):
        if obj.user and hasattr(obj.user, 'profile'):
            return obj.user.profile.room_number or '-'
        return '-'
    get_room_number.short_description = 'Комната'

    def get_room_number_display(self, obj):
        if obj.user and hasattr(obj.user, 'profile'):
            return obj.user.profile.room_number or '-'
        return '-'
    get_room_number_display.short_description = 'Комната'

    actions = ['mark_as_in_progress', 'mark_as_completed', 'mark_as_new']

    def mark_as_new(self, request, queryset):
        queryset.update(status=Appeal.STATUS_NEW)
        self.message_user(request, f'Обращения помечены как "Новые"')
    mark_as_new.short_description = 'Отметить как "Новые"'

    def mark_as_in_progress(self, request, queryset):
        queryset.update(status=Appeal.STATUS_IN_PROGRESS)
        self.message_user(request, f'Обращения помечены как "В работе"')
    mark_as_in_progress.short_description = 'Отметить как "В работе"'

    def mark_as_completed(self, request, queryset):
        queryset.update(status=Appeal.STATUS_COMPLETED)
        self.message_user(request, f'Обращения помечены как "Завершено"')
    mark_as_completed.short_description = 'Отметить как "Завершено"'