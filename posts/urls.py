from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('post/create/', views.create_post_view, name='create_post'),
    path('post/<int:post_id>/like/', views.like_post_toggle, name='like_post'),
    path('post/<int:post_id>/comment/', views.comment_post_view, name='comment_post'),

    # REST Framework endpoints
    path('api/posts/', views.PostListAPIView.as_view(), name='api_post_list'),
    path('api/posts/<int:pk>/', views.PostDetailAPIView.as_view(), name='api_post_detail'),
]
