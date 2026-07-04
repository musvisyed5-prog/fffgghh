import django_filters
from allauth.socialaccount import providers
from django.db.models import Q
from django import forms
from django.utils.translation import gettext_lazy as _


from job.models import (
    JobPosting,
    JobApplicant
)
from job.choices import (
    JOB_TYPE,
    STATUS_CHOICES
)


def get_provider_choices():
    provider_classes = providers.registry.get_class_list()
    return [(p.id, p.name) for p in provider_classes]

class JobPostingFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        method='general_search',
        label='',
        widget=forms.TextInput(attrs={
           "placeholder":  _('Search for roles, companies, or platforms'),
           "class": "flex-1 w-full"
        })
    )
    platform = django_filters.ChoiceFilter(
        choices=get_provider_choices(),
        lookup_expr="iexact",
        empty_label=_("Platform")
    )
    type = django_filters.ChoiceFilter(
        choices=JOB_TYPE,
        empty_label=_("Type")
    )

    class Meta:
        model = JobPosting
        fields = {
            "type",
            "platform",
        }

    def general_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(location__icontains=value) |
            Q(company__name__icontains=value) |
            Q(platform__icontains=value)
        )


class JobApplicationFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        method='general_search',
        label='',
        widget=forms.TextInput(attrs={
           "placeholder":  _('Search by job name'),
           "class": "flex-1 w-full"
        })
    )
    status = django_filters.ChoiceFilter(
        choices=STATUS_CHOICES,
        empty_label=_("Status")
    )

    class Meta:
        model = JobApplicant
        fields = [
            'status'
        ]


    def general_search(self, queryset, name, value):
        return queryset.filter(Q(job__title__icontains=value) )
    

class JobApplicantFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        method='general_search',
        label='',
        widget=forms.TextInput(attrs={
           "placeholder":  _('Search by Applicant name'),
           "class": "flex-1 w-full"
        })
    )

    status = django_filters.ChoiceFilter(
        choices=STATUS_CHOICES,
        empty_label=_("Status")
    )

    
    class Meta:
        model = JobApplicant
        fields = [
            'status'
        ]


    def general_search(self, queryset, name, value):
        return queryset.filter(
            Q(applicant__first_name__icontains=value)|
            Q(applicant__last_name__icontains=value)
        )