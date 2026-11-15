from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Comment, Like


class UserMiniSerializer(serializers.ModelSerializer):
    avatar_url = serializers.ReadOnlyField(source='profile.avatar_url')
    display_name = serializers.ReadOnlyField(source='profile.display_name')

    class Meta:
        model = User
        fields = ('id', 'username', 'display_name', 'avatar_url')


class CommentSerializer(serializers.ModelSerializer):
    author = UserMiniSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'author', 'content', 'created_at')
        read_only_fields = ('id', 'author', 'created_at')


class PostSerializer(serializers.ModelSerializer):
    author = UserMiniSerializer(read_only=True)
    likes_count = serializers.ReadOnlyField()
    comments_count = serializers.ReadOnlyField()
    comments = CommentSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id', 'author', 'caption', 'image', 'created_at',
            'likes_count', 'comments_count', 'comments', 'is_liked'
        )
        read_only_fields = ('id', 'author', 'created_at')

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
