from django.db import models
from django.conf import settings


class Appeal(models.Model):
    STATUS_NEW = "new"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"

    STATUS_CHOICES = [
        (STATUS_NEW, "Новое"),
        (STATUS_IN_PROGRESS, "В работе"),
        (STATUS_COMPLETED, "Завершено"),
    ]

    SPECIALIST_CHOICES = [
        ("plumber", "Сантехник"),
        ("carpenter", "Плотник"),
        ("electrician", "Электрик"),
        ("other", "Другое"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appeals",
    )
    subject = models.CharField("Тема", max_length=120)
    specialist = models.CharField("Специалист", max_length=20, choices=SPECIALIST_CHOICES)
    message = models.TextField("Обращение", max_length=1000)
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NEW,
    )
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Обращение"
        verbose_name_plural = "Обращения"
        permissions = [
            ("can_view_all_appeals", "Может просматривать все обращения"),
            ("can_change_appeal_status", "Может изменять статус обращений"),
            ("can_assign_specialist", "Может назначать специалиста"),
        ]

    def __str__(self):
        return f"{self.subject} ({self.get_status_display()})"