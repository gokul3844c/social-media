from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import Q
from .models import Follow, Notification


@login_required
@require_POST
def follow_toggle_view(request, username):
    """
    Toggle follow status for a user. Supports AJAX JSON responses.
    """
    target_user = get_object_or_404(User, username=username)

    if target_user == request.user:
        return JsonResponse({'error': 'You cannot follow yourself.'}, status=400)

    follow_instance = Follow.objects.filter(follower=request.user, following=target_user).first()

    if follow_instance:
        follow_instance.delete()
        is_following = False
    else:
        Follow.objects.create(follower=request.user, following=target_user)
        is_following = True

        # Create notification
        Notification.objects.create(
            recipient=target_user,
            sender=request.user,
            notification_type='follow'
        )

    followers_count = target_user.followers_set.count()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
        return JsonResponse({
            'success': True,
            'is_following': is_following,
            'followers_count': followers_count,
            'username': target_user.username
        })

    return redirect(request.META.get('HTTP_REFERER', 'profile', username=username))


def search_view(request):
    """
    Search accounts by username, display name, or bio.
    """
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        results = User.objects.filter(
            Q(username__icontains=query) |
            Q(profile__full_name__icontains=query) |
            Q(profile__bio__icontains=query)
        ).select_related('profile').distinct()[:20]

    return render(request, 'social/search.html', {'query': query, 'results': results})


@login_required
def notifications_view(request):
    """
    List user notifications and mark unread notifications as read.
    """
    notifications = request.user.notifications.select_related(
        'sender', 'sender__profile', 'post'
    ).all()[:50]

    # Mark as read
    request.user.notifications.filter(is_read=False).update(is_read=True)

    return render(request, 'social/notifications.html', {'notifications': notifications})
