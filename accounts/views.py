from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm, ProfileEditForm
from .models import Profile


def register_view(request):
    """
    Handle user registration at /register/.
    Validates all fields, hashes password via Django auth, creates profile,
    and redirects to login upon success.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f"Registration successful! You can now sign in as @{user.username}."
            )
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors indicated below.")
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    Handle user login at /login/ with Django sessions and secure cookies.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f"Welcome back, @{user.username}!")
            next_url = request.GET.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@require_POST
def logout_view(request):
    """
    Handle logout using POST with CSRF protection.
    """
    if request.user.is_authenticated:
        username = request.user.username
        auth_logout(request)
        messages.info(request, f"You have been signed out, @{username}.")
    return redirect('login')


@login_required(login_url='login')
def current_user_profile_view(request):
    """
    Direct route to /profile/ for the currently authenticated user.
    """
    return render_user_profile(request, request.user)


def profile_view(request, username):
    """
    Public profile route at /users/<username>/.
    """
    user_obj = get_object_or_404(User.objects.select_related('profile'), username=username)
    return render_user_profile(request, user_obj)


def render_user_profile(request, user_obj):
    """
    Reusable helper to render a user's profile with stats and posts.
    """
    profile, _ = Profile.objects.get_or_create(user=user_obj)

    # Gather user's posts
    posts = user_obj.posts.all().select_related('author').prefetch_related('likes', 'comments')
    posts_count = posts.count()

    # Followers and following counts
    followers_count = user_obj.followers_set.count() if hasattr(user_obj, 'followers_set') else 0
    following_count = user_obj.following_set.count() if hasattr(user_obj, 'following_set') else 0

    is_self = (request.user.is_authenticated and request.user == user_obj)
    is_following = False
    if request.user.is_authenticated and not is_self and hasattr(user_obj, 'followers_set'):
        is_following = user_obj.followers_set.filter(follower=request.user).exists()

    context = {
        'profile_user': user_obj,
        'profile': profile,
        'posts': posts,
        'posts_count': posts_count,
        'followers_count': followers_count,
        'following_count': following_count,
        'is_following': is_following,
        'is_self': is_self,
    }
    return render(request, 'accounts/profile.html', context)


@login_required(login_url='login')
def profile_edit_view(request):
    """
    Edit profile at /profile/edit/ for the authenticated user only.
    """
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('current_profile')
        else:
            messages.error(request, "Please fix the errors below to update your profile.")
    else:
        form = ProfileEditForm(instance=profile)

    return render(request, 'accounts/profile_edit.html', {
        'form': form,
        'profile': profile
    })
