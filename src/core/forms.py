from django import forms
from django.contrib.auth.forms import (
    UserCreationForm as BaseUserCreationForm, 
    UserChangeForm as BaseUserChangeForm
)
from django.utils.translation import gettext_lazy as _
from allauth.account.forms import SignupForm as AllAuthSignupForm
from django.forms import ValidationError

from core.models import User
from src.validators import (
    name_valditors,
    picture_extension_validator
)

class UserCreationForm(BaseUserCreationForm):
    class Meta:
        model = User
        fields = ("email", "groups")


class UserChangeForm(BaseUserChangeForm):
    class Meta:
        model = User
        exclude = ['username']


class SignupForm(AllAuthSignupForm):
    first_name = forms.CharField(
        max_length=150, 
        required=True,
        label=_("first name"),
        validators=[name_valditors],
        widget=forms.TextInput(attrs={'placeholder': _('First name')})
    )
    last_name = forms.CharField(
        max_length=150, 
        required=True,
        label=_("last name"),
        validators=[name_valditors],
        widget=forms.TextInput(attrs={'placeholder': _('Last name')})
    )
    profile_picture = forms.ImageField(
        required=True,
        label=_("Profile picture"),
        validators=[picture_extension_validator]
    )


    def clean_email(self):
        email = self.cleaned_data["email"]           
        blocked_mail_providers = [
            'gmail',
            'outlook',
            'yahoo',
            'protonmail',
            'zoho',
            'iCloud'
        ]
        extract_mail_provider = email.lower().split('@')[1].split('.')[0]

        if extract_mail_provider not in blocked_mail_providers:
            return super().clean_email()
        raise ValidationError(
            _(f'email provider restricted: {blocked_mail_providers}'))

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.profile_picture = request.FILES["profile_picture"]
        user.save(update_fields=["first_name", "last_name", "profile_picture"])
        return user
    