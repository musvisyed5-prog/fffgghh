from django.utils import timezone
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
import uuid
from auditlog.registry import auditlog


from job.choices import (
    JOB_TYPE,
    STATUS_CHOICES
)
from company.models import Company
from src.validators import text_validator


User = get_user_model()


class JobPosting(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        primary_key=True
    )
    recruter = models.ForeignKey(
        User,
        verbose_name=_('user'),
        on_delete=models.CASCADE,
        related_name='recruter_jobposting_related',
        related_query_name='recruter_jobposting_query',
        limit_choices_to={'groups__name__in': ['company', 'creator']}
    )

    title = models.CharField(
        _('job title'),
        max_length=225,
        null=False,
        blank=False,
        validators=[text_validator]
    )
    type = models.CharField(
        _('job type'),
        max_length=2,
        choices=JOB_TYPE,
        default='FT'
    )
    desc = models.TextField(
        _('job description'),
        validators=[text_validator]
    )
    requirements = models.TextField(
        _('job requirements and skills'),
        null=False,
        blank=False,
        validators=[text_validator]
    )

    company = models.ForeignKey(
        Company,
        verbose_name=_('company'),
        on_delete=models.CASCADE,
        related_name='company_jobposting_related',
        related_query_name='company_jobposting_query',
        null=True,
        blank=True,
    )
    platform = models.CharField(
        _('job platform'),
        help_text=_('The platform this job is connected to. ')
    )
    location = models.CharField(
        _('job location'),
        null=False,
        blank=False,
        validators=[text_validator]
    )

    salary_min = models.DecimalField(
        _('minmum salary'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    salary_max = models.DecimalField(
        _('maximum salary'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    exp_min = models.DecimalField(
        _('minmum experience in years'),
        default=0,
        max_digits=12,
        decimal_places=2,
    )
    exp_max = models.DecimalField(
        _('maximum experience in years'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    tags = models.CharField(
        _("tags (optional)"),
        null=True,
        blank=True,
        help_text=_("use ',' to seprate tags"),
    )

    date_created = models.DateTimeField(
        _('date created'),
        auto_now_add=True
    )
    date_expires = models.DateTimeField(
        _("date expires"),
        help_text=_(
            "The date and time until which this job remains publicly visible.")
    )
    date_updated = models.DateTimeField(
        _("date updated"),
        auto_now=True
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_(
            "Uncheck to deactivate this job posting without deleting it.")
    )

    class Meta:
        ordering = ['-date_created']
        verbose_name = _("job Posting")
        verbose_name_plural = _("job Postings")

    def __str__(self):
        return str(_(f"{self.title}"))

    @property
    def days_left(self):
        if not self.date_expires:
            return None

        delta = self.date_expires - timezone.now()
        return max(delta.days, 0)

    @property
    def is_open(self):
        return (
            self.is_active
            and self.date_expires
            and self.date_expires > timezone.now()
        )

    @property
    def recruter_profile(self):
        return self.recruter.linked_account_details(self.recruter, self.platform)


class CustomQuestion(models.Model):
    job = models.OneToOneField(
        JobPosting,
        verbose_name=_('user'),
        on_delete=models.CASCADE,
        related_name='job_customquestion_related',
        related_query_name='job_customquestion_query',
    )
    structure = models.JSONField(
        _("form structure"),
        null=False,
        blank=False
    )
    date_created = models.DateTimeField(
        _('date created'),
        auto_now_add=True
    )
    date_updated = models.DateTimeField(
        _("date updated"),
        auto_now=True
    )

    class Meta:
        verbose_name = _('question')
        verbose_name_plural = _('questions')
        ordering = ["-date_created", "-date_updated"]

    def __str__(self):
        return str(self.id)


class JobApplicant(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        primary_key=True
    )
    job = models.ForeignKey(
        JobPosting,
        verbose_name=_('job'),
        on_delete=models.CASCADE,
        related_name='job_jobapplicant_related',
        related_query_name='job_jobapplicant_query',
    )
    applicant = models.ForeignKey(
        User,
        verbose_name=_('applicant'),
        on_delete=models.CASCADE,
        related_name='applicant_jobapplicant_related',
        related_query_name='applicant_jobapplicant_query',
        limit_choices_to={'groups__name__in': ['talent']}
    )
    answer = models.JSONField(
        _("answer"),
        null=True,
        blank=True
    )
    status = models.CharField(
        _("Application status"),
        choices=STATUS_CHOICES,
        default='APPLIED'
    )
    status_reason = models.TextField(
        _("Description"),
        null=True,
        blank=False
    )
    date_created = models.DateTimeField(
        _('date created'),
        auto_now_add=True
    )
    date_updated = models.DateTimeField(
        _("date updated"),
        auto_now=True
    )

    class Meta:
        verbose_name = _('job applicant')
        verbose_name_plural = _('job applicants')
        ordering = ["-date_updated", "-date_created"]

    def __str__(self):
        return str(self.id)


auditlog.register(JobPosting)
auditlog.register(CustomQuestion)
auditlog.register(JobApplicant)
