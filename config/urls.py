"""
SocialSphere URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Phase 2 Core Authentication & Profile Routes
    path('register/', accounts_views.register_view, name='register'),
    path('login/', accounts_views.login_view, name='login'),
    path('logout/', accounts_views.logout_view, name='logout'),
    path('profile/', accounts_views.current_user_profile_view, name='current_profile'),
    path('profile/edit/', accounts_views.profile_edit_view, name='profile_edit'),
    path('users/<str:username>/', accounts_views.profile_view, name='profile'),
    path('users/<str:username>/', accounts_views.profile_view, name='user_profile'),

    # App Namespaces and Legacy compatibility
    path('accounts/', include('accounts.urls')),
    path('social/', include('social.urls')),
    path('', include('posts.urls')),
    path('api-auth/', include('rest_framework.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
