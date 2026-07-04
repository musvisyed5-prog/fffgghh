from django.utils.translation import gettext_lazy as _


FEEDBACK_CATEGORIES = [
    ("BUG", _("Bug Report")),
    ("FEA", _("Feature Request")),
    ("GEN", _("General Feedback")),
    ("SUP", _("Support")),
]

REPORT_CATEGORIES = [
    ("SPM", _("Spam")),
    ("HST", _("Harassment")),
    ("FAP", _("Fake Profile")),
    ("INAP", _("Inappropriate Content")),
    ("SCAM", _("Scam or Fraud")),
    ("OTH", _("Others")),
]

REPORT_STATUS = [
    ("PEN", _("Pending")),
    ("REV", _("Reviewed")),
    ("RES", _("Resolved")),
    ("REJ", _("Rejected")),
]