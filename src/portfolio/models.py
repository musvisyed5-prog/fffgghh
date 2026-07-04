import re
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict
from uuid import uuid4
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from multiselectfield import MultiSelectField
from auditlog.registry import auditlog

from portfolio.choices import (
    TALENT_SPECIALIZATION_CHOICES,
    VIDEO_PLATFORM_CHOICES
)
from portfolio.utils import Api

User = get_user_model()


class Experience(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_experience_related',
        related_query_name='user_experience_query',
    )
    title = models.CharField(
        _('title '),
        max_length=100
    )
    frm = models.DateField(
        _("from (optional)"),
    )
    to = models.DateField(
        _("to (optional)"),
        null=True,
        blank=True
    )
    description = models.TextField(
        _('description'),
        null=True,
        blank=True
    )
    is_present = models.BooleanField(
        _("Presently wokring"),
        default=False
    )

    def __str__(self):
        return f"{self.title})"

    class Meta:
        verbose_name = _('experiance')
        verbose_name_plural = _('experiances')


class Language(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('language')
        verbose_name_plural = _('languages')


class Video(models.Model):
    id = models.UUIDField(
        default=uuid4,
        primary_key=True,
        unique=True,
        editable=False
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_video_related',
        related_query_name='user_video_query',
    )
    title = models.CharField(
        max_length=100,
        blank=True
    )

    link = models.URLField(
        help_text="Paste YouTube, Vimeo, or other video link",
        null=False,
        blank=False
    )
    desc = models.TextField(
        _("description"),
        null=True,
        blank=True,
    )

    role = MultiSelectField(
        _("Specialization"),
        max_length=100,
        choices=TALENT_SPECIALIZATION_CHOICES,
    )
    platform = models.CharField(
        _('platform'),
        max_length=100,
        choices=VIDEO_PLATFORM_CHOICES,
        default='youtube'
    )

    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        User,
        verbose_name=_('Verifier'),
        on_delete=models.CASCADE,
        related_name='verified_by_videos_related',
        related_query_name='verified_by_videos_query',
        limit_choices_to={'groups__name__in': ['creator']},
        null=True,
        blank=True
    )
    verified_at = models.DateTimeField(
        null=True,
        blank=True
    )
    extra_data = models.JSONField(
        _("video data"),
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = _('video')
        verbose_name_plural = _('vidoes')
        permissions = [
            ("can_verify", _("Can Verify this video")),
            ("can_view_verified_work", _("Can View Verified work")),
        ]

    def get_first_role_display(self):
        if self.role:
            return dict(TALENT_SPECIALIZATION_CHOICES).get(self.role[0])
        return None

    def get_video_id(self):
        url = self.link

        patterns = {
            "youtube": [
                r"youtu\.be/([^?&/]+)",
                r"v=([^?&]+)",
                r"youtube\.com/shorts/([^?&/]+)",
            ],
            "twitch": [
                r"twitch\.tv/videos/(\d+)",
                r"clips\.twitch\.tv/([^?&/]+)",
            ],
            "instagram": [
                r"instagram\.com/reels/([^/?&]+)",
                r"instagram\.com/p/([^/?&]+)",
            ],
            "discord": [
                r"channels/(\d+)/(\d+)",  # guild_id, channel_id
                r"attachments/\d+/(\d+)",  # message_id (better)
            ]
        }

        for platform, regex_list in patterns.items():
            for pattern in regex_list:
                match = re.search(pattern, url)
                if match:
                    if platform == "discord" and len(match.groups()) == 2:
                        return {
                            "guild_id": match.group(1),
                            "channel_id": match.group(2)
                        }
                    return match.group(1)

        return None

    def get_video_detail(self):
        api = Api(
            user=self.user,
            provider=self.platform
        )
        id = self.get_video_id()
        data = api.request_video_data(id=id)
        return data
    
    def get_thumb(self):
        if not self.extra_data:
            return None
        
        if self.platform == 'youtube':
            return self.extra_data.get('thumbnails', {}).get('maxres').get('url', None)

        elif self.platform == 'twitch':
            url = self.extra_data.get('thumbnail_url', None).replace("%{width}", "1280").replace("%{height}", "720")
            return url
        
        
    def get_title(self):
        if not self.extra_data:
            return self.title

        return self.extra_data.get('title', self.title)
    
    def save(self, *args, **kwargs):
        if not self.extra_data and self.platform != 'discord':
            self.extra_data = self.get_video_detail()
        super().save(*args, **kwargs)


class Portfolio(models.Model):
    public_id = models.IntegerField(
        unique=True,
        editable=False,
    )
    user = models.OneToOneField(
        User,
        verbose_name=_('user'),
        on_delete=models.CASCADE,
        related_name='user_portfolio_related',
        related_query_name='user_portfolio_query',
        limit_choices_to={'groups__name__in': ['talent']}
    )

    roles = MultiSelectField(
        _("Specialization"),
        max_length=100,
        choices=TALENT_SPECIALIZATION_CHOICES,
        help_text=_(
            "Choose your primary talent first. It will be displayed on your profile.")
    )

    about = models.TextField(
        _("about"),
        null=False,
        blank=False,
    )

    experiences = models.ManyToManyField(
        Experience,
        blank=True,
        verbose_name=_("experiences"),
        related_name='experiences_portfolio_related',
        related_query_name='experiences_portfolio_query',
    )

    languages = models.ManyToManyField(
        Language,
        blank=True,
        verbose_name=_("languages"),
        related_name='languages_portfolio_related',
        related_query_name='languages_portfolio_query',
    )
    videos = models.ManyToManyField(
        Video,
        blank=True,
        verbose_name=_("videos"),
        related_name='videos_portfolio_related',
        related_query_name='videos_portfolio_query',
    )

    date_updated = models.DateTimeField(
        _("date updated"),
        auto_now=True,
    )

    def save(self, *args, **kwargs):
        if not self.public_id:
            self.public_id = self.user.public_id
        super().save(*args, **kwargs)

    def __str__(self):
        return str(_(f"{self.public_id}"))

    @property
    def roles_display(self):
        choices = dict(TALENT_SPECIALIZATION_CHOICES)
        return [choices.get(role, role) for role in self.roles]

    def get_first_role_display(self):
        if self.roles:
            return dict(TALENT_SPECIALIZATION_CHOICES).get(self.roles[0])
        return None
    
    @property
    def get_platform_count(self):
        return Video.objects.filter(user=self.user).values('platform').distinct().count()

    TIER_ORDER = {
        "Bronze": 1,
        "Silver": 2,
        "Gold": 3,
        "Diamond": 4
    }

    def get_badge_summary(self):
        histories = self.user.user_badgehistory_related.order_by("-created_at")
        

        grouped = defaultdict(list)

        for history in histories:
            (tier, count) = history.video.verified_by.get_stats(history.video)

            key = (history.video.platform, tier)

            grouped[key].append({
                "date": history.created_at,
                "count": count
            })

        grouped_list = []

        for (platform, tier), items in grouped.items():
            grouped_list.append({
                "platform": platform,
                "tier": tier,
                "count": len(items),
                "history": items
            })

        # sort highest tier first
        grouped_list.sort(
            key=lambda x: self.TIER_ORDER.get(x["tier"], 0),
            reverse=True
        )
        return grouped_list

    class Meta:
        verbose_name = _("portfolio")
        verbose_name_plural = _("portfolios")


class BagdesHistory(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name=_('user'),
        on_delete=models.CASCADE,
        related_name='user_badgehistory_related',
        related_query_name='user_badgehistory_query',
        limit_choices_to={'groups__name__in': ['talent']}
    )
    video = models.ForeignKey(
        Video,
        verbose_name=_('video'),
        on_delete=models.CASCADE,
        related_name='video_badgehistory_related',
        related_query_name='video_badgehistory_query',
        limit_choices_to={"is_verified": True}
    )

    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("badge history")
        verbose_name_plural = _("badge history")

    def __str__(self):
        return str(self.id)


class Point(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name=_('user'),
        on_delete=models.CASCADE,
        related_name='user_point_related',
        related_query_name='user_point_query',
        limit_choices_to={'groups__name__in': ['creator']}
    )
    video = models.ForeignKey(
        Video,
        verbose_name=_('video'),
        on_delete=models.CASCADE,
        related_name='video_point_related',
        related_query_name='video_point_query',
        limit_choices_to={"is_verified": True}
    )
    point_value = models.DecimalField(
        _("point"),
        max_digits=5,
        decimal_places=2,
        default=0
    )

    date_expire = models.DateTimeField(
        _("expire date")
    )
    date_created = models.DateTimeField(
        auto_now=True
    )

    is_redeemed = models.BooleanField(
        _("redeemed"),
        default=False,
    )

    class Meta:
        verbose_name = _("point")
        verbose_name_plural = _("point's")

    def __str__(self):
        return str(self.id)

    @property
    def is_expired(self):
        return timezone.now() > self.date_expire
    
    @property
    def days_left(self):
        if not self.date_expire:
            return None

        delta = self.date_expire - timezone.now()
        return max(delta.days, 0)

    def save(self, *args, **kwargs):
        if not self.date_expire:
            self.date_expire = timezone.now() + timedelta(days=60)
        super().save(*args, **kwargs)

