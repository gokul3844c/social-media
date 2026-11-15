import os
from PIL import Image
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Profile


class UserRegistrationForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Full Name',
            'autocomplete': 'name',
            'id': 'reg-full-name',
        }),
        error_messages={
            'required': 'Please enter your full name.',
            'max_length': 'Full name cannot exceed 150 characters.'
        }
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Email address',
            'autocomplete': 'email',
            'id': 'reg-email',
        }),
        error_messages={
            'required': 'Please provide an email address.',
            'invalid': 'Please enter a valid email address.'
        }
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password',
            'autocomplete': 'new-password',
            'id': 'reg-password',
        }),
        error_messages={
            'required': 'Please enter a password.'
        }
    )
    password_confirm = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm Password',
            'autocomplete': 'new-password',
            'id': 'reg-password-confirm',
        }),
        error_messages={
            'required': 'Please confirm your password.'
        }
    )

    class Meta:
        model = User
        fields = ('username', 'email')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Username',
                'autocomplete': 'username',
                'id': 'reg-username',
            }),
        }
        error_messages = {
            'username': {
                'required': 'Please choose a username.',
            }
        }

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not username:
            raise ValidationError("Username cannot be empty.")
        if len(username) < 3:
            raise ValidationError("Username must be at least 3 characters long.")
        if ' ' in username:
            raise ValidationError("Username cannot contain spaces.")
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("A user with that username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise ValidationError("Email address is required.")
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with that email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm:
            if password != password_confirm:
                self.add_error('password_confirm', "Passwords do not match.")
            else:
                # Apply Django password validators
                try:
                    temp_user = User(
                        username=cleaned_data.get('username', ''),
                        email=cleaned_data.get('email', '')
                    )
                    validate_password(password, temp_user)
                except ValidationError as e:
                    for error in e.error_list:
                        self.add_error('password', error)

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            full_name = self.cleaned_data.get('full_name')
            if full_name:
                profile.full_name = full_name
                profile.save()
        return user


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Username',
            'autocomplete': 'username',
            'id': 'login-username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password',
            'autocomplete': 'current-password',
            'id': 'login-password',
        })
    )

    error_messages = {
        'invalid_login': "Invalid username or password. Please try again.",
        'inactive': "This account is inactive.",
    }


class ProfileEditForm(forms.ModelForm):
    MAX_IMAGE_SIZE_MB = 5
    ALLOWED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.gif')
    ALLOWED_FORMATS = ('JPEG', 'PNG', 'WEBP', 'GIF')

    full_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Full Name',
            'id': 'edit-fullname',
        })
    )
    bio = forms.CharField(
        max_length=350,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input form-textarea',
            'placeholder': 'Tell the world about yourself...',
            'rows': 3,
            'maxlength': '350',
            'id': 'edit-bio',
        })
    )
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-file-input',
            'accept': 'image/jpeg,image/png,image/webp,image/gif',
            'id': 'edit-profile-picture-input',
        }),
        error_messages={
            'invalid_image': 'The uploaded file is corrupt or is not a valid image.'
        }
    )

    class Meta:
        model = Profile
        fields = ('full_name', 'bio', 'profile_picture')

    def clean_bio(self):
        bio = self.cleaned_data.get('bio', '')
        if len(bio) > 350:
            raise ValidationError("Biography cannot exceed 350 characters.")
        return bio

    def clean(self):
        cleaned_data = super().clean()

        # Check raw uploaded file size before processing
        uploaded_file = self.files.get('profile_picture')
        if uploaded_file and uploaded_file.size > self.MAX_IMAGE_SIZE_MB * 1024 * 1024:
            self.add_error(
                'profile_picture',
                f"Image file size cannot exceed {self.MAX_IMAGE_SIZE_MB}MB."
            )

        return cleaned_data

    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')
        if not picture or not hasattr(picture, 'file'):
            return picture

        # 1. Enforce file size limit
        if picture.size > self.MAX_IMAGE_SIZE_MB * 1024 * 1024:
            raise ValidationError(
                f"Image file size cannot exceed {self.MAX_IMAGE_SIZE_MB}MB."
            )

        # 2. Check file extension
        ext = os.path.splitext(picture.name)[1].lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise ValidationError(
                f"Unsupported file format '{ext}'. Allowed: JPG, PNG, WEBP, GIF."
            )

        # 3. Verify actual image binary content with Pillow
        try:
            image = Image.open(picture)
            image.verify()

            if image.format not in self.ALLOWED_FORMATS:
                raise ValidationError(
                    f"Invalid image type ({image.format}). Allowed: JPEG, PNG, WEBP, GIF."
                )
        except Exception:
            raise ValidationError("The uploaded file is corrupt or is not a valid image.")
        finally:
            if hasattr(picture, 'seek'):
                picture.seek(0)

        return picture
