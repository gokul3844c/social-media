from django import forms
from .models import Post, Comment


class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('caption', 'image')
        widgets = {
            'caption': forms.Textarea(attrs={
                'class': 'form-input form-textarea',
                'placeholder': 'What are you thinking? Share with your sphere...',
                'rows': 3,
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-file-input',
                'accept': 'image/*',
                'id': 'post-image-input',
            }),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'comment-input',
                'placeholder': 'Add a comment...',
                'autocomplete': 'off',
            }),
        }
