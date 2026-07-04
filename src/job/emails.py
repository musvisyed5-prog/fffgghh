from core.utils import BaseEmailServices
from django.urls import reverse
from django_tasks import task


from job.models import (
    JobApplicant,
    JobPosting
)

EmailService = BaseEmailServices()


@task()
def JOBFILLINGEMAIL(url, id):
    instance = JobApplicant.objects.select_related(
        "job",
        "applicant"
    ).get(pk=id)

    subject = f"Application Received: {instance.job.title}"
    base_url = url

    context = {
        "name": f"{instance.applicant.first_name} {instance.applicant.last_name}",
        "job_title": instance.job.title,
        "application_url": f"{base_url}{reverse('job:owned_applications')}",
    }

    EmailService.send(
        template="email/application_received.html",
        context=context,
        subject=subject,
        recipients=[instance.applicant.email],
    )


@task()
def JOBSTATUSEMAIL(url, applicant_id):
    instance = JobApplicant.objects.select_related(
        "job",
        "applicant"
    ).get(pk=applicant_id)


    subject = f"Update on your application for {instance.job.title}"
    base_url = url

    context = {
        "name": f"{instance.applicant.first_name} {instance.applicant.first_name}",
        "job_title": instance.job.title,
        "status": instance.get_status_display(),
        "reason": instance.status_reason,
        "application_url": f"{base_url}{reverse('job:owned_applications')}",
    }

    EmailService.send(
        template="email/status_update.html",
        context=context,
        subject=subject,
        recipients=[instance.applicant.email],
    )


@task()
def JOBCLOSEDEMAILTOAPPLICANTS(url, job_id):
    job = (
        JobPosting.objects
        .prefetch_related("job_jobapplicant_related__applicant")
        .get(pk=job_id)
    )


    if not job.job_jobapplicant_related.all():
        return

    base_url = url

    subject = f"Job Closed: {job.title}"

    for applicant in job.job_jobapplicant_related.all():
        context = {
            "name": f"{applicant.applicant.first_name} {applicant.applicant.last_name}",
            "job_title": job.title,
            "application_url": f"{base_url}{reverse('job:owned_applications')}",
        }

        EmailService.send(
            template="email/job_closed.html",
            context=context,
            subject=subject,
            recipients=[applicant.applicant.email],
        )
