from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from auditlog.registry import auditlog

User = get_user_model()

from company.choices import (
    COUNTRIES,
    COUNTRY_CODES,
    INDUSTRY_CHOICES
)
from company.validators import (
    phonenumber_validator,
    text_validator,
    address_validator
)

class PhoneNumber(models.Model):
    code = models.CharField(
        _("country code"),
        max_length=8,
        choices=COUNTRY_CODES,
        default='+91',
    )
    number = models.CharField(
        _("number"),
        max_length=15,
        null=True,
        blank=True,
        validators=[phonenumber_validator]
    )

    class Meta:
        verbose_name = _("phone number")
        verbose_name_plural = _("phone numbers")

    def __str__(self):
        return f"{self.code}{self.number}"



class Company(models.Model):
    user = models.OneToOneField(
        User,
        verbose_name=_('user'),
        on_delete=models.CASCADE,
        related_name='user_company_related',
        related_query_name='user_company_query',
        limit_choices_to={'groups__name__in':['company']}
    )
    slug = models.SlugField(
        _("slug"),
        editable=False,
        primary_key=True,
        unique=True
    )
    name = models.CharField(
        _('company name'),
        max_length=255,
        null=False,
        blank=False,
        validators=[text_validator]
    )
    tagline  = models.CharField(
        _("company tagline (Optional)"),
        null=True,
        blank=True
    )
    phone = models.ForeignKey(
        PhoneNumber,
        verbose_name=_("phone number"),
        on_delete=models.CASCADE,
        null=True,
        blank=False,
        related_name="phone_company_related",
        related_query_name="phone_company_query"
    )
    email = models.EmailField(
        _("company email address"),
    )
    country = models.CharField(
        _('country'),
        choices=COUNTRIES,
        default='IN'
    )
    address = models.TextField(
        _('company address'),
        max_length=500,
        null=False,
        blank=False,
        validators=[address_validator]
    )
    bio = models.TextField(
        _('company bio'),
        null=False,
        blank=False,
        validators=[text_validator]
    )
    url = models.URLField(
        _("company website url"),
        null=False,
        blank=False
    )
    industry = models.TextField(
        _('industry'),
        max_length=100,
        choices=INDUSTRY_CHOICES,
        default=''
    )
    employe_size = models.PositiveIntegerField(
        _("number of employe"),
        null=False,
        blank=False,
    )
    logo_url = models.URLField(
        _("company Logo url"),
        null=False,
        blank=False
    )
    is_listed = models.BooleanField(
        verbose_name=_("show on public listing"),
        default=True,
        help_text=_("if checked, this company will be visible to all users")
    )
    date_created = models.DateTimeField(
        _('date created'),
        auto_now_add=True
    )
    date_updated = models.DateTimeField(
        _("date updated"),
        auto_now=True,
    )

    def __str__(self):
        return str(_(f"{self.name}"))
    
    class Meta:
        verbose_name = _("company")
        verbose_name_plural = _("companies")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


auditlog.register(Company)