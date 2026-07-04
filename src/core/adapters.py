from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.utils.translation import gettext_lazy as _
from allauth.core.exceptions import ImmediateHttpResponse
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpRequest
from django.forms import ValidationError
from django.shortcuts import resolve_url

from core.models import User


def set_user_group(request: HttpRequest, group_name: str, user: User) -> None:
    """
        Assign the given user to a Django auth group and finalize role-based login state.

        This function:
        - Validates that a login role (group name) is provided
        - Ensures the target group exists (case-insensitive)
        - Assigns the user to the group if they are not already grouped
        - Sets the username based on the email prefix (first login only)
        - Clears the role information from the session

        If validation fails, the login/signup flow is immediately terminated
        using ImmediateHttpResponse with an error message and redirect.
    """

    if not group_name:
        messages.error(
            request,
            _('role is required')
        )
        raise ImmediateHttpResponse(redirect(request.path))

    try:
        group = Group.objects.get(name__iexact=group_name)
    except Group.DoesNotExist:
        raise ValidationError( 
             _(f"This account is registered as a {group_name}. Please log in as {group_name} ")
        )

    if not user.groups.exists():
        user.username = user.email.split('@')[0]
        user.groups.add(group)

    request.session.pop('group', None)
    request.session.modified = True


class AccountAdapter(DefaultAccountAdapter):
    """
    Account adapter for handling user registration and login workflows.
    This adapter extends Django's DefaultAccountAdapter to provide custom logic for:
    - User account creation with automatic group assignment
    - Pre-login validation including email provider checks and user group verification
    The adapter ensures that only users belonging to the 'company' group can log in,
    while allowing social login bypasses standard email validation checks.
    """

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        user.save()
        set_user_group(request=request, group_name='company', user=user)
        return user

    def authenticate(self, request, **credentials):
        user = super().authenticate(request, **credentials)

        if user:
            if not user.groups.filter(name="company").exists():
                raise ValidationError(_('login restricted for Company only'))
        return user
    
    def get_login_redirect_url(self, request):
        next_url = request.session.pop("next", None)

        if next_url:
            return resolve_url(next_url)
        return super().get_login_redirect_url(request)


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Assign user to group based on login role stored in session
    """

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        group_name = request.session.get('group')
        set_user_group(request=request, group_name=group_name, user=user)

        extra_data = sociallogin.account.extra_data
        user.first_name = extra_data.get('given_name', '')
        user.last_name = extra_data.get('family_name', '')
        return user

    def pre_social_login(self, request, sociallogin):
        request._is_social_login = True

        if not request.user.is_authenticated:
            login_group = (request.session.get('group') or '').lower()

            if not login_group:
                messages.error(
                    request,
                    _('session expired')
                )
                raise ImmediateHttpResponse(redirect('home'))

            if sociallogin.is_existing:
                user = sociallogin.user
                user_groups = {g.name.lower() for g in user.groups.all()}

                # Check: Is this a Company user trying to use Social Login?
                if 'company' in user_groups or login_group == 'company':
                    messages.error(
                        request,
                        _('email and password authentication required for company users')
                    )
                    raise ImmediateHttpResponse(redirect('account_login'))

                # Check: Does the user actually belong to the group they are trying to log in as?
                if login_group not in user_groups:
                    messages.error(
                        request,
                        _(f'This account is registered as a {user.groups.first().name}. Please log in as {user.groups.first().name.upper()} "')
                    )
                    raise ImmediateHttpResponse(redirect('home'))

        return super().pre_social_login(request, sociallogin)
