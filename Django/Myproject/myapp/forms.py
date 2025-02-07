from django import forms
from .models import Albumin
from .models import Profile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

class AlbuminForm(forms.ModelForm):
    class Meta:
        model = Albumin
        fields = ['title', 'description', 'sub_title', 'sub_content', 'image', 'category']
        widgets = {
            'sub_content': forms.Textarea(attrs={'rows': 3, 'cols': 20}),
        }

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required. Inform a valid email address.")
    phone_number = forms.CharField(max_length=15, required=False, help_text="Optional. Enter a valid phone number.")
    profile_picture = forms.ImageField(required=False)  # No 'multiple' attribute needed

    class Meta:
        model = get_user_model()  # Use the custom user model
        fields = ('username', 'email', 'phone_number', 'profile_picture', 'password1', 'password2')

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["profile_picture"]
        