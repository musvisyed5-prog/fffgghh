from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core.models import User
from core.forms import (
    UserCreationForm,
    UserChangeForm
)

from core.models import (
    Notification,
    Feedback,
    Report
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm

    exclude = ("username",)
    readonly_fields = ("date_updated", "last_login")
    list_display = [
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'is_superuser',
        'last_login'
    ]
    search_fields = [
        'public_id',
        'email',
        'first_name',
        'last_name',
    ]
    list_filter = [
        'is_active',
        'is_staff',
        'is_superuser',
        'language',
        'groups',
        'date_joined',
        'last_login'
    ]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {
         "fields": ("first_name", "last_name", "profile_picture")}),
        (_("Preferences"), {"fields": ("language", "extra_data")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {
         "fields": ("last_login", "date_joined", "date_updated")}),
    )

    # 🔑 OVERRIDE add_fieldsets (remove username)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    'groups',
                    'is_staff'
                ),
            },
        ),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'recipient',
        'title'
    ]

    search_fields = [
        'title',
        'recipient'
    ]
    list_filter = ['date_created']


@admin.register(Feedback)
class FeebackAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'date_created'
    ]
    search_fields = ['user']
    list_filter = ['date_created']


@admin.register(Report)
class RerportAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'reporter',
        'reason',
        'status',
        'date_created'
    ]
    search_fields = [
        'reporter',
        'id'
    ]
    list_filter = [
        'reason',
        'status',
        'date_created'
    ]
