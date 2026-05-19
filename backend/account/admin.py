from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    """Кастомная форма для профиля с полями из User"""
    first_name = forms.CharField(max_length=150, required=False, label='Имя')
    last_name = forms.CharField(max_length=150, required=False, label='Фамилия')
    email = forms.EmailField(required=False, label='Email')

    employee_group = forms.BooleanField(
        required=False,
        label='Сотрудник',
        help_text='Дать пользователю права сотрудника (доступ к заявкам и новостям)'
    )

    class Meta:
        model = UserProfile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['employee_group'].initial = self.instance.user.groups.filter(name='Сотрудник').exists()

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()
            user = profile.user
            user.first_name = self.cleaned_data.get('first_name', '')
            user.last_name = self.cleaned_data.get('last_name', '')
            user.email = self.cleaned_data.get('email', '')
            user.save()

            employee_group, created = Group.objects.get_or_create(name='Сотрудник')
            user_group, _ = Group.objects.get_or_create(name='Пользователь')

            if self.cleaned_data.get('employee_group'):
                user.groups.add(employee_group)
                user.groups.remove(user_group)
            else:
                user.groups.remove(employee_group)
                if not user.groups.filter(name='Пользователь').exists():
                    user.groups.add(user_group)
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

    list_display = ('username', 'email', 'first_name', 'last_name', 'get_groups',
                    'get_middle_name', 'get_room_number', 'get_phone',
                    'get_hostel', 'get_university', 'is_staff', 'is_active', 'employee_action')

    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'profile__hostel', 'profile__has_no_middle_name')

    search_fields = ('username', 'email', 'first_name', 'last_name',
                     'profile__room_number', 'profile__phone', 'profile__middle_name')

    def get_groups(self, obj):
        groups = [group.name for group in obj.groups.all()]
        if 'Сотрудник' in groups:
            return '👤 Сотрудник'
        return ', '.join(groups) or '-'

    get_groups.short_description = 'Роль'
    get_groups.admin_order_field = 'groups'

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

    def employee_action(self, obj):
        is_employee = obj.groups.filter(name='Сотрудник').exists()
        if is_employee:
            return format_html(
                '<a class="button" href="remove-employee/{}/" style="background: #ba2121; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none;">✖ Снять</a>',
                obj.id
            )
        else:
            return format_html(
                '<a class="button" href="make-employee/{}/" style="background: #0a5a0a; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none;">✓ Назначить</a>',
                obj.id
            )

    employee_action.short_description = 'Действие'
    employee_action.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('make-employee/<int:user_id>/', self.make_employee_view, name='make_employee'),
            path('remove-employee/<int:user_id>/', self.remove_employee_view, name='remove_employee'),
        ]
        return custom_urls + urls

    def make_employee_view(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
            employee_group, _ = Group.objects.get_or_create(name='Сотрудник')
            user_group, _ = Group.objects.get_or_create(name='Пользователь')
            user.groups.add(employee_group)
            user.groups.remove(user_group)
            user.save()
            messages.success(request, f'Пользователь {user.username} назначен сотрудником')
        except User.DoesNotExist:
            messages.error(request, 'Пользователь не найден')
        return redirect('admin:auth_user_changelist')

    def remove_employee_view(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
            employee_group = Group.objects.get(name='Сотрудник')
            user_group, _ = Group.objects.get_or_create(name='Пользователь')
            user.groups.remove(employee_group)
            if not user.groups.filter(name='Пользователь').exists():
                user.groups.add(user_group)
            user.save()
            messages.success(request, f'Пользователь {user.username} снят с должности сотрудника')
        except User.DoesNotExist:
            messages.error(request, 'Пользователь не найден')
        return redirect('admin:auth_user_changelist')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    inlines = [UserProfileInline]


class UserProfileAdmin(admin.ModelAdmin):
    form = UserProfileForm

    list_display = ('user', 'get_full_name', 'get_username', 'is_employee', 'employee_action',
                    'phone', 'hostel', 'room_number', 'university', 'avatar_preview')

    list_filter = ('has_no_middle_name', 'hostel', 'university')

    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name',
                     'room_number', 'phone', 'middle_name', 'university')

    list_per_page = 20

    readonly_fields = ('avatar_preview',)

    fieldsets = (
        ('Пользователь', {
            'fields': ('user',)
        }),
        ('Права доступа', {
            'fields': ('employee_group',),
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

    def get_username(self, obj):
        return obj.user.username

    get_username.short_description = 'Логин'
    get_username.admin_order_field = 'user__username'

    def is_employee(self, obj):
        return obj.user.groups.filter(name='Сотрудник').exists()

    is_employee.boolean = True
    is_employee.short_description = 'Сотрудник'

    def employee_action(self, obj):
        is_employee = obj.user.groups.filter(name='Сотрудник').exists()
        if is_employee:
            return format_html(
                '<a class="button" href="remove-employee/{}/" style="background: #ba2121; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none;">✖ Снять</a>',
                obj.user.id
            )
        else:
            return format_html(
                '<a class="button" href="make-employee/{}/" style="background: #0a5a0a; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none;">✓ Назначить</a>',
                obj.user.id
            )

    employee_action.short_description = 'Действие'
    employee_action.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('make-employee/<int:user_id>/', self.make_employee_view, name='make_employee_profile'),
            path('remove-employee/<int:user_id>/', self.remove_employee_view, name='remove_employee_profile'),
        ]
        return custom_urls + urls

    def make_employee_view(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
            employee_group, _ = Group.objects.get_or_create(name='Сотрудник')
            user_group, _ = Group.objects.get_or_create(name='Пользователь')
            user.groups.add(employee_group)
            user.groups.remove(user_group)
            user.save()
            messages.success(request, f'Пользователь {user.username} назначен сотрудником')
        except User.DoesNotExist:
            messages.error(request, 'Пользователь не найден')
        return redirect('admin:account_userprofile_changelist')

    def remove_employee_view(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
            employee_group = Group.objects.get(name='Сотрудник')
            user_group, _ = Group.objects.get_or_create(name='Пользователь')
            user.groups.remove(employee_group)
            if not user.groups.filter(name='Пользователь').exists():
                user.groups.add(user_group)
            user.save()
            messages.success(request, f'Пользователь {user.username} снят с должности сотрудника')
        except User.DoesNotExist:
            messages.error(request, 'Пользователь не найден')
        return redirect('admin:account_userprofile_changelist')

    def avatar_preview(self, obj):
        if obj.avatar and obj.avatar.url:
            return format_html('<img src="{}" style="max-width: 80px; max-height: 80px; border-radius: 8px;" />',
                               obj.avatar.url)
        return 'Нет аватара'

    avatar_preview.short_description = 'Превью аватара'

    actions = ['make_employee_bulk', 'remove_employee_bulk', 'mark_no_middle_name', 'clear_phone_numbers']

    def make_employee_bulk(self, request, queryset):
        employee_group, _ = Group.objects.get_or_create(name='Сотрудник')
        user_group, _ = Group.objects.get_or_create(name='Пользователь')
        for profile in queryset:
            user = profile.user
            user.groups.add(employee_group)
            user.groups.remove(user_group)
            user.save()
        self.message_user(request, f'Сотрудниками назначено {queryset.count()} пользователей')

    make_employee_bulk.short_description = 'Назначить сотрудниками (выбранные)'

    def remove_employee_bulk(self, request, queryset):
        employee_group = Group.objects.get(name='Сотрудник')
        user_group, _ = Group.objects.get_or_create(name='Пользователь')
        for profile in queryset:
            user = profile.user
            user.groups.remove(employee_group)
            if not user.groups.filter(name='Пользователь').exists():
                user.groups.add(user_group)
            user.save()
        self.message_user(request, f'Права сотрудника удалены у {queryset.count()} пользователей')

    remove_employee_bulk.short_description = 'Снять права сотрудника (выбранные)'

    def mark_no_middle_name(self, request, queryset):
        queryset.update(has_no_middle_name=True)
        self.message_user(request, f'У {queryset.count()} профилей отмечено "Нет отчества"')

    mark_no_middle_name.short_description = 'Отметить "Нет отчества"'

    def clear_phone_numbers(self, request, queryset):
        queryset.update(phone='')
        self.message_user(request, f'Телефоны очищены у {queryset.count()} профилей')

    clear_phone_numbers.short_description = 'Очистить номера телефонов'


class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_permissions_count')
    search_fields = ('name',)
    filter_horizontal = ('permissions',)

    def get_permissions_count(self, obj):
        return obj.permissions.count()

    get_permissions_count.short_description = 'Количество прав'


# Регистрация в админке
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)

admin.site.register(UserProfile, UserProfileAdmin)