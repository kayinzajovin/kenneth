from django import forms
from .models import UserProfile, Vehicle


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'role']
        