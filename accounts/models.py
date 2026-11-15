from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    """
    Custom profile linked one-to-one with Django's built-in User model.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    full_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(max_length=350, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/%Y/%m/', blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    website = models.URLField(max_length=200, blank=True)
    location = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username}'s profile"

    @property
    def display_name(self):
        if self.full_name:
            return self.full_name
        return self.user.get_full_name() or self.user.username

    @property
    def avatar_url(self):
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return '/static/images/default-avatar.svg'

    @property
    def profile_picture_url(self):
        return self.avatar_url
