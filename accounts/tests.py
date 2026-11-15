import io
from PIL import Image
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from accounts.models import Profile
from posts.models import Post, Like, Comment


def create_test_image(format='JPEG', size=(100, 100), color=(255, 0, 0)):
    """Helper to generate a real valid in-memory image using Pillow."""
    file_obj = io.BytesIO()
    image = Image.new('RGB', size, color)
    image.save(file_obj, format=format)
    file_obj.seek(0)
    extension = 'jpg' if format == 'JPEG' else format.lower()
    return SimpleUploadedFile(
        f'test_image.{extension}',
        file_obj.read(),
        content_type=f'image/{extension}'
    )


class SocialSpherePhase2Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='alex_creator',
            email='alex@example.com',
            password='ComplexPassword123!'
        )
        self.user.profile.full_name = 'Alex Morgan'
        self.user.profile.bio = 'Digital nomad & creative photographer.'
        self.user.profile.save()

        self.post = Post.objects.create(
            author=self.user,
            caption='First testing moment'
        )

    # 1. Registration Tests
    def test_registration_success(self):
        """Valid registration creates User & Profile and redirects to /login/."""
        response = self.client.post(reverse('register'), {
            'username': 'new_user',
            'email': 'new_user@example.com',
            'full_name': 'New Creator',
            'password': 'SecurePassword987!',
            'password_confirm': 'SecurePassword987!',
        }, follow=True)

        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='new_user').exists())

        new_user = User.objects.get(username='new_user')
        self.assertTrue(new_user.check_password('SecurePassword987!'))
        self.assertEqual(new_user.profile.full_name, 'New Creator')
        self.assertContains(response, 'Registration successful')

    def test_registration_duplicate_username(self):
        """Registration rejects duplicate usernames."""
        response = self.client.post(reverse('register'), {
            'username': 'alex_creator',  # already exists
            'email': 'unique@example.com',
            'full_name': 'Another Alex',
            'password': 'SecurePassword987!',
            'password_confirm': 'SecurePassword987!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'username',
            'A user with that username already exists.'
        )

    def test_registration_duplicate_email(self):
        """Registration rejects duplicate emails."""
        response = self.client.post(reverse('register'), {
            'username': 'different_user',
            'email': 'alex@example.com',  # already registered
            'full_name': 'Diff User',
            'password': 'SecurePassword987!',
            'password_confirm': 'SecurePassword987!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'email',
            'An account with that email already exists.'
        )

    def test_registration_mismatched_passwords(self):
        """Registration rejects mismatched password and confirmation."""
        response = self.client.post(reverse('register'), {
            'username': 'mismatch_user',
            'email': 'mismatch@example.com',
            'full_name': 'Mismatch User',
            'password': 'SecurePassword987!',
            'password_confirm': 'WrongPassword987!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'password_confirm',
            'Passwords do not match.'
        )

    # 2. Login and Logout Tests
    def test_login_success(self):
        """Valid login authenticates user, establishes session, and redirects to home."""
        response = self.client.post(reverse('login'), {
            'username': 'alex_creator',
            'password': 'ComplexPassword123!',
        }, follow=True)

        self.assertRedirects(response, reverse('home'))
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertEqual(response.context['user'].username, 'alex_creator')

    def test_login_invalid_credentials(self):
        """Invalid credentials show generic error and keep user unauthenticated."""
        response = self.client.post(reverse('login'), {
            'username': 'alex_creator',
            'password': 'WrongPassword!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password. Please try again.')

    def test_authenticated_user_redirected_from_auth_pages(self):
        """Logged-in users visiting login or register are redirected to home."""
        self.client.login(username='alex_creator', password='ComplexPassword123!')

        resp_login = self.client.get(reverse('login'))
        self.assertRedirects(resp_login, reverse('home'))

        resp_register = self.client.get(reverse('register'))
        self.assertRedirects(resp_register, reverse('home'))

    def test_logout_post_required(self):
        """Logout must be a POST request; GET request is rejected with 405."""
        self.client.login(username='alex_creator', password='ComplexPassword123!')

        # GET should fail
        get_resp = self.client.get(reverse('logout'))
        self.assertEqual(get_resp.status_code, 405)

        # POST should succeed
        post_resp = self.client.post(reverse('logout'), follow=True)
        self.assertRedirects(post_resp, reverse('login'))
        self.assertFalse(post_resp.context['user'].is_authenticated)

    # 3. Profile Viewing Tests
    def test_unauthenticated_current_profile_redirect(self):
        """Accessing /profile/ without login redirects to /login/?next=/profile/."""
        response = self.client.get(reverse('current_profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_authenticated_current_profile_view(self):
        """Logged-in user visiting /profile/ sees their own profile."""
        self.client.login(username='alex_creator', password='ComplexPassword123!')
        response = self.client.get(reverse('current_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'alex_creator')
        self.assertContains(response, 'Edit Profile')
        self.assertContains(response, 'Joined')

    def test_public_user_profile_view(self):
        """Public view /users/<username>/ works for any user."""
        response = self.client.get(reverse('profile', kwargs={'username': 'alex_creator'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'alex_creator')
        self.assertContains(response, 'Digital nomad')

    # 4. Profile Editing & Image Validation Tests
    def test_profile_edit_unauthorized_redirect(self):
        """Unauthenticated user visiting /profile/edit/ is redirected to login."""
        response = self.client.get(reverse('profile_edit'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_profile_edit_success_with_valid_image(self):
        """Authenticated user can update full_name, bio, and upload a valid picture."""
        self.client.login(username='alex_creator', password='ComplexPassword123!')

        test_img = create_test_image(format='PNG', size=(80, 80))
        response = self.client.post(reverse('profile_edit'), {
            'full_name': 'Alexander The Great',
            'bio': 'Updated bio for testing purposes.',
            'profile_picture': test_img,
        }, follow=True)

        self.assertRedirects(response, reverse('current_profile'))
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.full_name, 'Alexander The Great')
        self.assertEqual(self.user.profile.bio, 'Updated bio for testing purposes.')
        self.assertTrue(bool(self.user.profile.profile_picture))

    def test_profile_edit_preserves_picture_when_empty(self):
        """Preserves existing profile picture when no new file is submitted."""
        self.client.login(username='alex_creator', password='ComplexPassword123!')

        # Set an initial picture
        test_img = create_test_image(format='JPEG', size=(50, 50))
        self.user.profile.profile_picture = test_img
        self.user.profile.save()
        initial_pic_name = self.user.profile.profile_picture.name

        # Edit only text fields
        response = self.client.post(reverse('profile_edit'), {
            'full_name': 'Only Name Changed',
            'bio': 'Keep the same picture.',
        }, follow=True)

        self.assertRedirects(response, reverse('current_profile'))
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.full_name, 'Only Name Changed')
        self.assertEqual(self.user.profile.profile_picture.name, initial_pic_name)

    def test_profile_edit_rejects_corrupted_fake_image(self):
        """Rejects files that are not valid images even if named .png (Pillow verification)."""
        self.client.login(username='alex_creator', password='ComplexPassword123!')

        fake_file = SimpleUploadedFile(
            'fake_image.png',
            b'NOT_A_REAL_IMAGE_DATA_CONTENT',
            content_type='image/png'
        )

        response = self.client.post(reverse('profile_edit'), {
            'full_name': 'Hacker Attempt',
            'bio': 'Testing corrupted file injection.',
            'profile_picture': fake_file,
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            'The uploaded file is corrupt or is not a valid image.',
            response.context['form'].errors['profile_picture']
        )

    def test_profile_edit_rejects_oversized_image(self):
        """Rejects files exceeding the 5MB size limit."""
        self.client.login(username='alex_creator', password='ComplexPassword123!')

        # 6MB dummy content
        oversized_data = b'x' * (6 * 1024 * 1024)
        oversized_file = SimpleUploadedFile(
            'huge.jpg',
            oversized_data,
            content_type='image/jpeg'
        )

        response = self.client.post(reverse('profile_edit'), {
            'full_name': 'Oversized Attempt',
            'profile_picture': oversized_file,
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            'Image file size cannot exceed 5MB.',
            response.context['form'].errors['profile_picture']
        )
