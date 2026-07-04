from django.utils.translation import gettext_lazy as _


JOB_TYPE = (
    ('FT', _('Full time')),
    ('PT', _('Part time')),
    ('CT', _('Contract')),
    ('RM', _('Remote')),
)

STATUS_CHOICES = [
    ("APPLIED", _("Applied")),
    ("UNDER_REVIEW", _("Under Review")),
    ("SHORTLISTED", _("Shortlisted")),
    ("INTERVIEW", _("Interview Scheduled")),
    ("REJECTED", _("Rejected")),
    ("HIRED", _("Hired")),
]