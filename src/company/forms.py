from django import forms
from django.utils.translation import gettext_lazy as _


from company.models import (
    Company
)
from company.choices import COUNTRY_CODES
from company.validators import phonenumber_validator
from src.services.forms import AITextarea

class CompanyUpdateAndRegistationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        ai_rewrite_limit_used = kwargs.pop("ai_rewrite_limit_used", 0)
        super().__init__(*args, **kwargs)

        if "bio" in self.fields:
            self.fields["bio"].widget.ai_rewrite_limit_used = ai_rewrite_limit_used

    code = forms.ChoiceField(
        label=_("country code"),
        choices=COUNTRY_CODES,
        initial="IN",
        required=True
    )
    number = forms.CharField(
        label=_("number"),
        max_length=15,
        required=True,
        validators=[phonenumber_validator]
    )

    class Meta:
        model = Company
        exclude = ['user', 'phone', 'is_listed']
        widgets = {
            "bio": AITextarea(attrs={"rows": 8,})
        }