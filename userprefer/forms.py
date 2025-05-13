from .models import UserProfile
from django import forms
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio']  # remove 'photo'
