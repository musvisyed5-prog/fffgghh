from django.contrib import admin


from job.models import (
    JobPosting,
    CustomQuestion,
    JobApplicant
)


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'type',
        'is_active',
        'platform',
        'location',
        'date_created',
        'date_updated'
    ]
    search_fields = [
        'title',
        'company',
        'recruter',
        'location',
        'platform',
    ]
    list_filter = [
        'date_created',
        'date_updated',
        'date_expires',
        'is_active'
    ]
    readonly_fields = [
        'date_created',
        'date_updated'
    ]


@admin.register(CustomQuestion)
class CustomQuestionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'date_created',
        'date_updated',
    ]
    list_filter = [
        'date_created',
        'date_updated'
    ]


@admin.register(JobApplicant)
class JobApplicantAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'status',
        'date_created',
        'date_updated'
    ]
    search_fields = [
        'id',
        'job',
        'applicant'
    ]
    list_filter = [
        'status',
        'date_created',
        'date_updated'
    ]
