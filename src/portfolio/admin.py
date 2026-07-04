from django.contrib import admin

from portfolio.models import (
    Experience,
    Language,
    Video,
    Portfolio,
    BagdesHistory,
    Point
)


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False


@admin.register(Video)
class VideosAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'is_verified',
        'verified_by',
        'created_at'
    ]
    search_fields = [
        'id',
        'user',
        'verified_by'
    ]
    list_filter = [
        'is_verified',
        'verified_at',
        'created_at'
    ]


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = [
        'public_id',
        'user',
        'date_updated'
    ]
    list_display_links = [
        'public_id'
    ]
    search_fields = [
        'user',
        'public_id'
    ]
    list_filter = [
        'roles'
    ]


@admin.register(BagdesHistory)
class BadgeHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'video',
        'created_at'
    ]
    search_fields = [
        'user',
        'video',
    ]
    search_fields = [
        'user',
        'video'
    ]
    list_filter = [
        'created_at'
    ]


@admin.register(Point)
class PointAdmin(admin.ModelAdmin):
    pass
