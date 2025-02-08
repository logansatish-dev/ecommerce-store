from django import forms
from django.contrib.auth.models import User
from .models import Review  # Ensure correct import

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Passwords do not match.")
        return cleaned_data  # Ensure cleaned data is returned

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review  # Ensure this is correctly set
        fields = ['rating', 'comment']
