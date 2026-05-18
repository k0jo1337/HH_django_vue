from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from PIL import Image
import os


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    middle_name = models.CharField('Отчество', max_length=150, blank=True)
    has_no_middle_name = models.BooleanField('Нет отчества', default=False)
    room_number = models.CharField('Номер комнаты', max_length=20)
    phone = models.CharField('Номер телефона', max_length=11, blank=True, default='')
    university = models.CharField('Институт', max_length=100, blank=True, default='')
    hostel = models.CharField('Номер общежития', max_length=20, blank=True, default='')
    avatar = models.ImageField(
        default='avatars/default.png',
        upload_to='avatars/',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f"{self.user.username} - room {self.room_number}"

    def save(self, *args, **kwargs):
        if isinstance(self.has_no_middle_name, str):
            self.has_no_middle_name = self.has_no_middle_name.lower() in ['true', '1', 'yes', 'on']

        super().save(*args, **kwargs)

        if self.avatar and self.avatar.name and self.avatar.name != 'avatars/default.png':
            try:
                if os.path.exists(self.avatar.path):
                    img = Image.open(self.avatar.path)
                    if img.height > 300 or img.width > 300:
                        output_size = (300, 300)
                        img.thumbnail(output_size)
                        img.save(self.avatar.path)
            except Exception as e:
                print(f"Error processing avatar: {e}")


# Сигнал для создания групп и прав после миграции
@receiver(post_migrate)
def create_groups_and_permissions(sender, **kwargs):
    if sender.name != 'account':
        return

    # Создаем группы
    employee_group, _ = Group.objects.get_or_create(name='Сотрудник')
    user_group, _ = Group.objects.get_or_create(name='Пользователь')

    # Пытаемся добавить права для обращений (если модель уже существует)
    try:
        from django.apps import apps
        Appeal = apps.get_model('api', 'Appeal')
        if Appeal:
            appeal_content_type = ContentType.objects.get_for_model(Appeal)

            # Права для сотрудников
            permission_codenames = [
                'can_view_all_appeals',
                'can_change_appeal_status',
                'can_assign_specialist'
            ]

            for codename in permission_codenames:
                try:
                    permission = Permission.objects.get(codename=codename, content_type=appeal_content_type)
                    employee_group.permissions.add(permission)
                except Permission.DoesNotExist:
                    pass
    except:
        pass