from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Appeal",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("subject", models.CharField(max_length=120, verbose_name="Тема")),
                (
                    "specialist",
                    models.CharField(
                        choices=[
                            ("plumber", "Сантехник"),
                            ("carpenter", "Плотник"),
                            ("electrician", "Электрик"),
                            ("other", "Другое"),
                        ],
                        max_length=20,
                        verbose_name="Специалист",
                    ),
                ),
                ("message", models.TextField(max_length=1000, verbose_name="Обращение")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("new", "Новое"),
                            ("in_progress", "В работе"),
                            ("completed", "Завершено"),
                        ],
                        default="new",
                        max_length=20,
                        verbose_name="Статус",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создано")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлено")),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="appeals",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Обращение",
                "verbose_name_plural": "Обращения",
                "ordering": ["-created_at"],
            },
        ),
    ]
