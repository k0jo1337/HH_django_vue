from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    """Кастомная форма для профиля с полями из User"""
    first_name = forms.CharField(max_length=150, required=False, label='Имя')
    last_name = forms.CharField(max_length=150, required=False, label='Фамилия')
    email = forms.EmailField(required=False, label='Email')

    class Meta:
        model = UserProfile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()
            # Сохраняем данные пользователя
            user = profile.user
            user.first_name = self.cleaned_data.get('first_name', '')
            user.last_name = self.cleaned_data.get('last_name', '')
            user.email = self.cleaned_data.get('email', '')
            user.save()
        return profile


class UserProfileInline(admin.StackedInline):
    """Встраиваемый профиль в страницу пользователя"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль пользователя'
    extra = 0

    fieldsets = (
        ('Личная информация', {
            'fields': ('middle_name', 'has_no_middle_name', 'phone', 'avatar_preview', 'avatar')
        }),
        ('Проживание', {
            'fields': ('room_number', 'hostel', 'university')
        }),
    )

    readonly_fields = ('avatar_preview',)

    def avatar_preview(self, obj):
        if obj.avatar and obj.avatar.url:
            return format_html('<img src="{}" style="max-width: 100px; max-height: 100px; border-radius: 8px;" />',
                               obj.avatar.url)
        return 'Нет аватара'

    avatar_preview.short_description = 'Текущий аватар'


class CustomUserAdmin(UserAdmin):
    """Кастомная админка для пользователей"""

    list_display = ('username', 'email', 'first_name', 'last_name',
                    'get_middle_name', 'get_room_number', 'get_phone',
                    'get_hostel', 'get_university', 'is_staff')

    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__hostel', 'profile__has_no_middle_name')

    search_fields = ('username', 'email', 'first_name', 'last_name',
                     'profile__room_number', 'profile__phone', 'profile__middle_name')

    def get_middle_name(self, obj):
        if hasattr(obj, 'profile'):
            if obj.profile.has_no_middle_name:
                return 'Нет отчества'
            return obj.profile.middle_name or '-'
        return '-'

    get_middle_name.short_description = 'Отчество'

    def get_room_number(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.room_number or '-'
        return '-'

    get_room_number.short_description = 'Комната'

    def get_phone(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.phone or '-'
        return '-'

    get_phone.short_description = 'Телефон'

    def get_hostel(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.hostel or '-'
        return '-'

    get_hostel.short_description = 'Общежитие'

    def get_university(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.university or '-'
        return '-'

    get_university.short_description = 'Институт'

    inlines = [UserProfileInline]


class UserProfileAdmin(admin.ModelAdmin):
    """Админка для профилей пользователей"""
    form = UserProfileForm

    list_display = ('user', 'get_full_name', 'phone', 'hostel', 'room_number',
                    'university', 'avatar_preview')

    list_filter = ('has_no_middle_name', 'hostel', 'university')

    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name',
                     'room_number', 'phone', 'middle_name', 'university')

    list_editable = ('room_number', 'phone', 'hostel', 'university')

    list_per_page = 20

    readonly_fields = ('avatar_preview',)

    fieldsets = (
        ('Пользователь', {
            'fields': ('user',)
        }),
        ('Личная информация', {
            'fields': ('first_name', 'last_name', 'middle_name', 'email', 'phone', 'avatar_preview', 'avatar')
        }),
        ('Проживание', {
            'fields': ('room_number', 'hostel', 'university')
        }),
    )

    def get_full_name(self, obj):
        return f"{obj.user.last_name} {obj.user.first_name} {obj.middle_name}".strip()

    get_full_name.short_description = 'Полное имя'
    get_full_name.admin_order_field = 'user__last_name'

    def avatar_preview(self, obj):
        if obj.avatar and obj.avatar.url:
            return format_html('<img src="{}" style="max-width: 80px; max-height: 80px; border-radius: 8px;" />',
                               obj.avatar.url)
        return 'Нет аватара'

    avatar_preview.short_description = 'Превью аватара'

    actions = ['mark_no_middle_name', 'clear_phone_numbers']

    def clear_phone_numbers(self, request, queryset):
        queryset.update(phone='')
        self.message_user(request, f'Телефоны очищены у {queryset.count()} профилей')

    clear_phone_numbers.short_description = 'Очистить номера телефонов'


# Перерегистрируем модель User с кастомной админкой
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Зарегистрируем профиль
admin.site.register(UserProfile, UserProfileAdmin)
