# By: Tsz Kit Wong
# File: wt_scrooge_capital/forms.py

# This file has all the forms used in the app

from django import forms
from .models import Stock, UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Username",
        label_suffix=""
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Password",
        label_suffix=""
    )


class SignupForm(UserCreationForm):
    """
        A form that extends UserCreationForm to include fields for UserProfile.
    """
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="First Name",
        label_suffix=""
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Last Name",
        label_suffix=""
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label="Email",
        label_suffix=""
    )
    dob = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Date of Birth",
        label_suffix=""
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email']

    def save(self, commit=True):
        # Save the User instance
        user = super().save(commit=False)
        if commit:
            user.save()
            # Create and link the UserProfile
            UserProfile.objects.create(
                user=user,
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                email=self.cleaned_data['email'],
                dob=self.cleaned_data['dob']
            )
        return user
    

class UpdateProfileForm(forms.ModelForm):
    """
        Form for updating a profile
    """

    dob = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Date of Birth",
        label_suffix=""
    )
    
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'email', 'dob']


class BuySellForm(forms.Form):
    """
        Form for buying or selling stocks
    """
    stock = forms.ModelChoiceField(queryset=Stock.objects.all(), label="Stock")
    action = forms.ChoiceField(choices=[('buy', 'Buy'), ('sell', 'Sell')], label="Action")
    shares = forms.IntegerField(min_value=1, label="Shares")