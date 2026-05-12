from django.contrib.auth.models import User
from django.db import models
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
        # Убеждаемся, что has_no_middle_name это булево значение
        if isinstance(self.has_no_middle_name, str):
            self.has_no_middle_name = self.has_no_middle_name.lower() in ['true', '1', 'yes', 'on']

        super().save(*args, **kwargs)

        # Оптимизация аватара
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