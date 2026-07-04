from core.utils import BaseEmailServices
from django_tasks import task

EmailService = BaseEmailServices()


@task()
def WelcomeTalentEmail(name: str, email: str):
    subject = f"You're in. Here's how to stand out on Arclent."
    context = {"name": f"{name}"}

    EmailService.send(
        template="email/welcome_talent.html",
        subject=subject,
        recipients=[email],
        context=context,
    )


@task()
def WelcomeCreatorCompanyEmail(name: str, email: str):
    subject = f"Your Arclent recruiter account is live."
    context = {"name": f"{name}"}

    EmailService.send(
        template="email/welcome_creatorcompany.html",
        subject=subject,
        recipients=[email],
        context=context,
    )
