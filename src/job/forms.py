from django import forms
from allauth.socialaccount.models import SocialAccount
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.urls import reverse_lazy



from job.models import (
    JobPosting
)
from src.services.forms import AITextarea


class JobPostingForm(forms.ModelForm):

    class Meta:
        model = JobPosting
        exclude = [
            'recruter',
            'company',
            'is_active'
        ]
        widgets = {
            "platform": forms.Select(),
            "desc": AITextarea(attrs={"rows": 5}),
            "requirements": AITextarea(attrs={"rows": 5}),
            'date_expires': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        ai_rewrite_limit_used = kwargs.pop("ai_rewrite_limit_used", 0)
        super().__init__(*args, **kwargs)

        providers = SocialAccount.objects.filter(
            user=user
        ).values_list("provider", flat=True)

        choices = [
             (p, "YouTube" if p == "google" else p.capitalize())
            for p in providers 
        ]

        if not choices:
            choices = [("", _("no platform connected"))]

        if "desc" in self.fields:
            self.fields["desc"].widget.ai_rewrite_limit_used = ai_rewrite_limit_used

        if "requirements" in self.fields:
            self.fields["requirements"].widget.ai_rewrite_limit_used = ai_rewrite_limit_used

        self.fields["platform"] = forms.ChoiceField(
            choices=choices,
            label=_('Job platform'),
            help_text=mark_safe(
                'Need to connect account? '
                '<a href="/account/3rdparty/" target="_blank">'
                'Connect here</a>'
            ),
            widget=forms.Select(attrs={'class': 'form-control'})
        )
