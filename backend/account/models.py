from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    middle_name = models.CharField(max_length=150, blank=True)
    has_no_middle_name = models.BooleanField(default=False)
    room_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.username} - room {self.room_number}"
