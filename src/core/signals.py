from django.contrib.auth.models import Group
from django.dispatch import receiver
from django.db.models.signals import m2m_changed
from django.contrib.auth import get_user_model


from core.emails import (
    WelcomeTalentEmail,
    WelcomeCreatorCompanyEmail
)
from portfolio.models import Portfolio


User = get_user_model()


@receiver(m2m_changed, sender=User.groups.through)
def UserSignals(sender, instance, action, pk_set, **kwargs):

    if action == "post_add":

        talent_group = Group.objects.filter(name="talent").first()

        if talent_group and talent_group.pk in pk_set:
            _, created = Portfolio.objects.get_or_create(user=instance)

            if created:
                WelcomeTalentEmail.enqueue(
                    name=instance.first_name,
                    email=instance.email,
                )
        
        else:
            WelcomeCreatorCompanyEmail.enqueue(
                name=instance.first_name,
                email=instance.email,
            )