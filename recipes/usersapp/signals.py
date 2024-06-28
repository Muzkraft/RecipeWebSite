from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile
import logging

logger = logging.getLogger(__name__)

"""
Автоматическое создание профилей (модель Profile) при регистрации пользователя на сайте
"""


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    try:
        if created:
            Profile.objects.create(user=instance)
    except Exception as e:
        logger.error(f"An error occurred while creating profile for user {instance.username}: {str(e)}")


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Exception as e:
        logger.error(f"An error occurred while saving profile for user {instance.username}: {str(e)}")