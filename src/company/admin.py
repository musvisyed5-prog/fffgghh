from django.contrib import admin

from company.models import (
    PhoneNumber,
    Company
)


@admin.register(PhoneNumber)
class PhoneAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'phone',
        'country',
        'is_listed',
        'date_created',
        'date_updated',
    ]
    search_fields = [
        'name',
        'industry',
        'address',
        'user__first_name',
        'user__last_name',
        'phone__number',
    ]
    list_filter = [
        'is_listed',
        'date_created',
        'date_updated',
    ]
    autocomplete_fields=['user']
    readonly_fields = [
        'date_created',
        'date_updated',
    ]