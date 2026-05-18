from django.db import models


class NewsPost(models.Model):
    title = models.CharField("Заголовок", max_length=160)
    summary = models.CharField("Краткое описание", max_length=280)
    content = models.TextField("Текст новости", blank=True)
    image = models.ImageField("Изображение", upload_to="news/", blank=True, null=True)
    is_published = models.BooleanField("Опубликовано", default=True)
    created_at = models.DateTimeField("Дата публикации", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Новость"
        verbose_name_plural = "Новости"

    def __str__(self):
        return self.title
