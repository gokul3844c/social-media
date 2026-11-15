from django.urls import path
from . import views

urlpatterns = [
    path('follow/<str:username>/', views.follow_toggle_view, name='follow_toggle'),
    path('search/', views.search_view, name='search'),
    path('notifications/', views.notifications_view, name='notifications'),
]
