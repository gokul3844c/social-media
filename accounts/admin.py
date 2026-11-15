from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'location', 'created_at')
    search_fields = ('user__username', 'user__email', 'full_name', 'bio', 'location')
    list_filter = ('created_at',)
