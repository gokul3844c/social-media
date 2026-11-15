from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from rest_framework import generics, permissions
from .models import Post, Like, Comment
from .forms import PostCreateForm, CommentForm
from .serializers import PostSerializer


def home_view(request):
    """
    Main feed view: displays stories, recent feed posts, quick composer,
    and suggested users sidebar.
    """
    posts = Post.objects.select_related('author', 'author__profile').prefetch_related(
        'likes', 'comments', 'comments__author', 'comments__author__profile'
    ).all()[:30]

    suggested_users = []
    liked_post_ids = set()

    if request.user.is_authenticated:
        # Exclude users already followed and current user
        following_ids = request.user.following_set.values_list('following_id', flat=True)
        suggested_users = User.objects.exclude(
            id__in=list(following_ids) + [request.user.id]
        ).select_related('profile')[:5]

        liked_post_ids = set(
            Like.objects.filter(user=request.user, post__in=posts).values_list('post_id', flat=True)
        )
    else:
        suggested_users = User.objects.all().select_related('profile')[:5]

    context = {
        'posts': posts,
        'suggested_users': suggested_users,
        'liked_post_ids': liked_post_ids,
        'post_form': PostCreateForm() if request.user.is_authenticated else None,
        'comment_form': CommentForm(),
    }
    return render(request, 'posts/home.html', context)


@login_required
@require_POST
def create_post_view(request):
    """
    Create a new post with image and/or caption.
    """
    form = PostCreateForm(request.POST, request.FILES)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        messages.success(request, "Your post is now live on SocialSphere!")
    else:
        messages.error(request, "Unable to publish post. Please check the image format and size.")
    return redirect('home')


@login_required
@require_POST
def like_post_toggle(request, post_id):
    """
    Toggle like on a post with JSON response for AJAX or redirect fallback.
    """
    post = get_object_or_404(Post, id=post_id)
    like_obj = Like.objects.filter(user=request.user, post=post).first()

    if like_obj:
        like_obj.delete()
        is_liked = False
    else:
        Like.objects.create(user=request.user, post=post)
        is_liked = True

        # Create notification if liking someone else's post
        if post.author != request.user:
            from social.models import Notification
            Notification.objects.create(
                recipient=post.author,
                sender=request.user,
                notification_type='like',
                post=post
            )

    likes_count = post.likes.count()

    # Support AJAX requests
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
        return JsonResponse({
            'success': True,
            'is_liked': is_liked,
            'likes_count': likes_count,
            'post_id': post.id
        })

    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
@require_POST
def comment_post_view(request, post_id):
    """
    Add a comment to a post.
    """
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()

        # Create notification if commenting on someone else's post
        if post.author != request.user:
            from social.models import Notification
            Notification.objects.create(
                recipient=post.author,
                sender=request.user,
                notification_type='comment',
                post=post
            )

        messages.success(request, "Comment added.")

    return redirect(request.META.get('HTTP_REFERER', 'home'))


# Django REST Framework API Views
class PostListAPIView(generics.ListCreateAPIView):
    """
    DRF API endpoint to list and create posts.
    """
    queryset = Post.objects.select_related('author', 'author__profile').prefetch_related('likes', 'comments').all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostDetailAPIView(generics.RetrieveAPIView):
    """
    DRF API endpoint to retrieve a single post.
    """
    queryset = Post.objects.select_related('author', 'author__profile').prefetch_related('likes', 'comments').all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
