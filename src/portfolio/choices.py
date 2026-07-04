from django.utils.translation import gettext_lazy as _

TALENT_SPECIALIZATION_CHOICES = [
    ("content_creator", _("Content Creator")),
    ("video_editor", _("Video Editor")),
    ("channel_manager", _("Channel / Account Manager")),
    ("live_streamer", _("Live Streamer")),
    ("community_manager", _("Community Manager")),
    ("moderator", _("Moderator")),
    ("growth_specialist", _("Growth Specialist")),
    ("social_media_manager", _("Social Media Manager")),
    ("ads_specialist", _("Ads / Performance Marketing Specialist")),
    ("brand_manager", _("Brand Manager")),
    ("script_writer", _("Script Writer")),
    ("thumbnail_designer", _("Thumbnail / Graphic Designer")),
    ("seo_specialist", _("SEO / Content Optimization Specialist")),
    ("analyst", _("Analytics & Insights Specialist")),
    ("multi_role", _("Multi-Role / Generalist")),
]


VIDEO_PLATFORM_CHOICES = [
    ("youtube", "YouTube"),
    ("discord", "Discord"),
    ("facebook", "Facebook"),
    ("instagram", "Instagram"),
    ("twitch", "Twitch"),
]