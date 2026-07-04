from django.core.validators import (
    FileExtensionValidator,
    RegexValidator
)
from django.utils.translation import gettext_lazy as _

picture_extension_validator = FileExtensionValidator(
    allowed_extensions=['png', 'jpg', 'jpeg', 'giff'],
    message=_('only ".png", ".jpg"," .jpeg", ".giff" are allowed')
)

name_valditors = RegexValidator(
    regex='^[a-zA-Z]+$',
    message=_('only letters without space, hypen are allowed')
)

text_validator = RegexValidator(
    regex=r"^[\s\S]+$",
    message=_("contains invalid characters.")
)