import secrets
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from allauth.socialaccount.models import SocialAccount
from auditlog.registry import auditlog

from core.utils import get_photo_path
from portfolio.utils import Verification
from src.validators import (
    picture_extension_validator,
    text_validator
)


from core.choices import (
    FEEDBACK_CATEGORIES,
    REPORT_CATEGORIES,
    REPORT_STATUS
)


class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(
                _("field 'email address' is required for user creation")
            )

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            username=email.split("@")[0],
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    public_id = models.IntegerField(
        _("pid"),
        unique=True,
        editable=False,
    )
    profile_picture = models.ImageField(
        _("profile picture"),
        upload_to=get_photo_path,
        null=True,
        blank=True,
        validators=[picture_extension_validator]
    )
    email = models.EmailField(
        _('email address'),
        null=False,
        blank=False,
        unique=True,
        error_messages={
            "unique": _("A user with that email already exists."),
        },
    )
    language = models.CharField(
        _("language"),
        max_length=10,
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE
    )

    date_updated = models.DateTimeField(
        _("date updated"),
        auto_now=True
    )

    extra_data = models.JSONField(
        _('extra data'),
        help_text=_("This field contain data of connected platform"),
        null=True,
        blank=True
    )

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.public_id:
            self.public_id = secrets.randbelow(90000000) + 10000000
        super().save(*args, **kwargs)

    @property
    def profile_image(self) -> str | None:
        """
        Return the user's profile image URL.

        Priority:
        1. Uploaded profile picture
        2. Social account picture
        3. None
        """

        if self.profile_picture:
            return self.profile_picture.url

        social = self.socialaccount_set.first()
        if social:
            return social.extra_data.get("picture")

        return None
    
    def linked_account_details(self, recruter, platform):
        context = {
            "image": recruter.profile_image,
            "name": f"{recruter.first_name} {recruter.last_name}".strip()
        }

        provider = 'google' if  platform.lower() == 'youtube' else platform

        try:
            # Use actual allauth provider names
            allauth_provider = provider

            account = SocialAccount.objects.filter(
                user=recruter,
                provider=allauth_provider
            ).first()

            if not account:
                return context

            data = account.extra_data

            if provider == "discord":
                avatar = data.get("avatar")
                user_id = data.get("id")

                if avatar and user_id:
                    context["image"] = (
                        f"https://cdn.discordapp.com/avatars/"
                        f"{user_id}/{avatar}.png"
                    )

                context["name"] = (
                    data.get("global_name")
                    or data.get("username")
                    or context["name"]
                )

            elif provider == "twitch":
                context["image"] = (
                    data.get("profile_image_url")
                    or context["image"]
                )
                context["name"] = (
                    data.get("display_name")
                    or context["name"]
                )

            elif provider == "google":
                get_set_channel_data = Verification(
                    user=recruter,
                    provider='youtube' if platform == 'google' else platform,
                    video=None
                )

                yt_data =get_set_channel_data.get_channel_data()[0]

                context["name"] = (
                    yt_data.get("snippet", {}).get('title')
                )
                context["image"] = (
                    yt_data.get('snippet', {}).get("thumbnails",{}).get('high', {}).get('url')
                )

        except KeyError:
            pass

        return context
    
    
    def get_stats(self, video):
        platform = video.platform
        if platform == "youtube":
            count = int(next(
                (
                    (channel.get("statistics") or {}).get("subscriberCount", 0)
                    for channel in self.extra_data.get(platform, [])
                    if channel.get("id") == video.extra_data.get("channelId")
                ),
                0
            ))

            if count >= 1_000_000:
                return "Diamond", count
            elif count >= 100_000:
                return "Gold", count
            elif count >= 10_000:
                return "Silver", count
            return "Bronze", count

        elif platform == "twitch":
            count = int(self.extra_data.get(platform, {}).get('statistics') or 0)

            if count >= 100_000:
                return "Diamond", count
            elif count >= 10_000:
                return "Gold", count
            elif count >= 1_000:
                return "Silver", count
            return "Bronze", count

        elif platform == "discord":
            count = int(next(
                    (
                        channel.get("approximate_member_count", 0)
                        for channel in self.extra_data.get(platform, [])
                        if (
                            str(channel.get("id")) == str(video.get_video_id().get("guild_id"))
                            and channel.get("owner") is True
                        )
                    ),
                    0
                ))
    
            if count >= 100_000:
                return "Diamond", count
            elif count >= 10_000:
                return "Gold", count
            elif count >= 1_000:
                return "Silver", count
            return "Bronze", count

        return "Bronze", 0



class Notification(models.Model):
    recipient = models.ForeignKey(
        User,
        verbose_name=_("recipient"),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='notification_recipient_related',
        related_query_name='notification_recipient_query',
    )
    title = models.CharField(
        _("title"),
        max_length=250,
        null=False,
        blank=False,
        validators=[text_validator]
    )
    msg = models.TextField(
        _('message'),
        null=False,
        blank=False,
        validators=[text_validator]
    )
    ahref = models.URLField(
        _("link"),
        null=True,
        blank=True
    )
    date_created = models.DateTimeField(
        _('date created'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _("notification")
        verbose_name_plural = _("notifications")
        ordering = ('-date_created',)

    def __str__(self):
        return f"Notification created"


class Feedback(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name=_('user'),
        on_delete=models.CASCADE,
        related_name='feedback_user_related',
        related_query_name='feedback_user_query',
    )
    category = models.CharField(
        max_length=20,
        choices=FEEDBACK_CATEGORIES,
    )
    subject = models.CharField(
        _("subject"),
        max_length=225,
        null=False,
        blank=False
    )
    desc = models.TextField(_("description"),)
    date_created = models.DateTimeField(
        _('date created'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _("feedback")
        verbose_name_plural = _("feedbacks")
        ordering = ('-date_created',)

    def __str__(self):
        return str(self.id)


class Report(models.Model):
    object_id = models.PositiveBigIntegerField(null=True)
    reporter = models.ForeignKey(
        User,
        verbose_name=_('user'),
        on_delete=models.CASCADE,
        related_name='report_user_related',
        related_query_name='report_user_query',
    )
    reason = models.CharField(
        _("Reason"),
        max_length=30,
        choices=REPORT_CATEGORIES
    )
    desc = models.TextField(
        _("description"),
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=REPORT_STATUS,
        default='PEN'
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    content_object = GenericForeignKey(
        "content_type",
        "object_id"
    )
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("report")
        verbose_name_plural = _("reports")
        ordering = ["-date_created"]

    def __str__(self):
        return str(self.id)


auditlog.register(Feedback)
auditlog.register(Report)
