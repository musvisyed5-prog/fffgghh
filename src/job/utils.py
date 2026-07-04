from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone


from job.models import (
    JobApplicant,
    JobPosting
)

def get_dashboard_anylatics(user: any):
    context = {}

    try:
        role = user.groups.all()[0].name

        if role == 'talent':
            applications = JobApplicant.objects.filter(applicant=user)

            context = {
                "role": role,
                "stats": applications.aggregate(
                    total=Count('id'),
                    applied=Count('id', filter=Q(status='APPLIED')),
                    shortlisted=Count('id', filter=Q(status='SHORTLISTED')),
                    rejected=Count('id', filter=Q(status='REJECTED')),
                ),

                "status_breakdown": list(
                    applications.values('status')
                    .annotate(count=Count('id'))
                ),

                "timeline": list(
                    applications
                    .annotate(date=TruncDate('date_created'))
                    .values('date')
                    .annotate(count=Count('id'))
                    .order_by('date')
                ),

                "recent": applications.select_related('job')[:5]
            }

        # -------------------------
        # 🏢 RECRUITER DASHBOARD
        # -------------------------
        elif role == 'creator' or role == 'company':
            jobs = JobPosting.objects.filter(recruter=user)
            applications = JobApplicant.objects.filter(job__in=jobs)

            context = {
                "role": role,
                "stats": {
                    "total_jobs": jobs.count(),
                    "active_jobs": jobs.filter(
                        is_active=True,
                        date_expires__gte=timezone.now()
                    ).count(),
                    "expired_jobs": jobs.filter(
                        date_expires__lt=timezone.now()
                    ).count(),
                },

                "app_stats": applications.aggregate(
                    total=Count('id'),
                    applied=Count('id', filter=Q(status='APPLIED')),
                    shortlisted=Count('id', filter=Q(status='SHORTLISTED')),
                    rejected=Count('id', filter=Q(status='REJECTED')),
                ),
                "job_performance": list(
                    JobApplicant.objects
                    .filter(job__recruter=user)
                    .values('job__id', 'job__title')
                    .annotate(app_count=Count('id'))
                    .order_by('-app_count')
                ),

                "timeline": list(
                    applications
                    .annotate(date=TruncDate('date_created'))
                    .values('date')
                    .annotate(count=Count('id'))
                    .order_by('date')
                ),

                "recent_applications": applications.select_related('job', 'applicant')[:5]
            }
    except Exception as e:
        pass
    return context
