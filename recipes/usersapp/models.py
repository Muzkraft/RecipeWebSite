from django.db import models
from django.contrib.auth.models import User
from PIL import Image
import logging

logger = logging.getLogger(__name__)


def user_directory_path(instance, filename):
    """
    Генерация пути, куда будет осуществлена загрузка изображения
    (MEDIA_ROOT/users_media/profile_pics/user_<id>/<filename>)
    """
    return 'users_media/profile_pics/user_{0}/{1}'.format(instance.user.id, filename)


class Profile(models.Model):
    user: User = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Домочадец")
    image = models.ImageField(default='вуафгде_avatar.jpg', upload_to=user_directory_path,
                              verbose_name="Аватар")

    class Meta:
        verbose_name = 'О домочадце'
        verbose_name_plural = 'О домочадцах'

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        """
        Переопределение метода save для сжатия загруженных пользователем аватарок,
        а также удаление старых аватарок, при их обновлении новыми
        """
        try:
            super().save(*args, **kwargs)

            # Допустимые расширения файла
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']

            if any(self.image.path.lower().endswith(ext) for ext in valid_extensions):
                # Проверка, что загруженный файл является изображением
                img = Image.open(self.image.path)

                if img.width > 240 or img.height > 240:
                    # Сжимаем изображение
                    output_size = (240, 240)
                    img.thumbnail(output_size)
                    img.save(self.image.path)
        except Exception as e:
            logger.error(f"An error occurred while saving profile image: {str(e)}")

    def delete(self, *args, **kwargs):
        """
        Переопределение метода delete для удаления изображения при удалении профиля
        """
        try:
            self.image.delete()
            super().delete(*args, **kwargs)
        except Exception as e:
            logger.error(f"An error occurred while deleting profile: {str(e)}")
