from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile


@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    """
    Ensure every User has an associated Profile upon creation and saving.
    """
    if created:
        Profile.objects.create(user=instance)
    else:
        # Use get_or_create to handle any legacy or superuser creation edge-cases
        Profile.objects.get_or_create(user=instance)
