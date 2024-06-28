from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core.files.storage import default_storage
from imagekit.models import ProcessedImageField, ImageSpecField
from imagekit.processors import ResizeToFit
import logging

logger = logging.getLogger(__name__)


class Category(models.Model):
    name = models.CharField(max_length=100, blank=False, verbose_name="Название категории")

    class Meta:
        verbose_name = 'Категория рецептов'
        verbose_name_plural = 'Категории рецептов'

    def __str__(self):
        return self.name


def user_directory_path(instance, filename):
    """
    Генерация пути, куда будет осуществлена загрузка изображения
    (MEDIA_ROOT/users_media/upload/user_<id>/<date>/<filename>)
    """
    now = timezone.now()
    today = now.strftime("%Y-%m-%d")
    return 'users_media/upload/user_{0}/{1}/{2}'.format(instance.author.id, today, filename)


class Recipe(models.Model):
    title = models.CharField(max_length=150, blank=False, verbose_name="Название блюда")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=False, verbose_name="Категория")
    description = models.TextField(blank=False, verbose_name="Описание")
    ingredients = models.TextField(blank=False, verbose_name="Ингредиенты")
    cooking_steps = models.TextField(blank=False, verbose_name="Шаги приготовления")
    cooking_time = models.DurationField(blank=False, verbose_name="Время приготовления (чч:мм:сс)")
    image = ProcessedImageField(upload_to=user_directory_path,
                                processors=[ResizeToFit(1024, 768)],
                                format='JPEG',
                                options={'quality': 90},
                                blank=False,
                                verbose_name="Изображение блюда")
    # Поле для показа миниатюр изображений блюда, чтобы не загружать изображение полностью
    image_thumbnail = ImageSpecField(source='image',
                                     processors=[ResizeToFit(100, 100)],
                                     format='JPEG',
                                     options={'quality': 90})
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, verbose_name="Автор рецепта")
    active = models.BooleanField(default=True, verbose_name="Статус активности")
    created_date = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """
        Перенаправление нового пользователя на отдельную страницу с рецептом
        """
        return reverse('recipe-detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        """
        Перед сохранением объекта, удаляем старое изображение
        """
        try:
            if self.pk:
                old_recipe = Recipe.objects.get(pk=self.pk)
                if self.image != old_recipe.image:
                    old_recipe.image.delete(save=False)
            super().save(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error saving recipe (ID: {self.pk}): {str(e)}")

    def delete(self, *args, **kwargs):
        """
        Переопределение метода delete для удаления изображения при удалении рецепта
        """
        try:
            default_storage.delete(self.image.name)
            default_storage.delete(self.image_thumbnail.name)
            super().delete(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error deleting recipe (ID: {self.pk}): {str(e)}")
