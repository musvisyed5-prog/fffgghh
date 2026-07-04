from django import forms
from django.forms import modelformset_factory

from src.services.forms import AITextarea
from portfolio.models import (
    Portfolio,
    Experience,
    Language,
    Video
)


class ExperienceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        ai_rewrite_limit_used = kwargs.pop("ai_rewrite_limit_used", 0)
        super().__init__(*args, **kwargs)

        if "description" in self.fields:
            self.fields["description"].widget.ai_rewrite_limit_used = ai_rewrite_limit_used

    class Meta:
        model = Experience
        exclude = ['user']
        widgets = {
            "description": AITextarea(attrs={"rows": 8, }),
            'frm': forms.DateInput(attrs={'type': 'date'}),
            'to': forms.DateInput(attrs={'type': 'date'}),
        }


class LanguageForm(forms.ModelForm):
    class Meta:
        model = Language
        fields = "__all__"


class PortfolioUpdatetForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        ai_rewrite_limit_used = kwargs.pop("ai_rewrite_limit_used", 0)
        super().__init__(*args, **kwargs)

        if "about" in self.fields:
            self.fields["about"].widget.ai_rewrite_limit_used = ai_rewrite_limit_used

    class Meta:
        model = Portfolio
        exclude = ['videos', 'user', 'experiences', 'languages']
        widgets = {
            "about": AITextarea(attrs={"rows": 8, })
        }


class VideoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        ai_rewrite_limit_used = kwargs.pop("ai_rewrite_limit_used", 0)
        super().__init__(*args, **kwargs)

        if "desc" in self.fields:
            self.fields["desc"].widget.ai_rewrite_limit_used = ai_rewrite_limit_used

    class Meta:
        model = Video
        exclude = (
            "user",
            "extra_data",
            "is_verified",
            "verified_by",
            "verified_at"
        )
        widgets = {
            "desc": AITextarea(attrs={"rows": 8, })
        }
