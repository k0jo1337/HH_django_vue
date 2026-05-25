from django.db import models
from django.conf import settings


class Executor(models.Model):
    """Модель исполнителя (сотрудника) без привязки к пользователю"""
    first_name = models.CharField("Имя", max_length=100)
    last_name = models.CharField("Фамилия", max_length=100)
    middle_name = models.CharField("Отчество", max_length=100, blank=True)
    position = models.CharField("Должность", max_length=100, blank=True)
    phone = models.CharField("Телефон", max_length=20, blank=True)
    work_phone = models.CharField("Рабочий телефон", max_length=20, blank=True)
    email = models.EmailField("Email", blank=True)
    is_active = models.BooleanField("Активен", default=True)
    created_at = models.DateTimeField("Дата добавления", auto_now_add=True)

    class Meta:
        verbose_name = "Исполнитель"
        verbose_name_plural = "Исполнители"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}".strip()

    def get_full_name(self):
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return " ".join(parts)


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
        verbose_name="Заявитель"
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
    executor = models.ForeignKey(
        Executor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appeals",
        verbose_name="Исполнитель"
    )
    completed_at = models.DateTimeField("Дата выполнения", null=True, blank=True)
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