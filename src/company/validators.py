from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


phonenumber_validator = RegexValidator(
    regex=r'^[1-9][0-9]{7,14}$',
    message=_('enter a valid phone number (8–15 digits)')
)

text_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9\s\/,\.\-\n]+$',
    message=_('some characters aren’t supported. Use only letters, numbers, and basic punctuation.')
)

address_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9\s/,\.\-\n]+$',
    message=_("check your address for typos or unsupported characters."),
    code='invalid_company_address'
)