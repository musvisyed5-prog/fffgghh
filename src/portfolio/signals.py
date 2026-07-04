from django.dispatch import receiver
from django.db.models.signals import post_save 

from portfolio.models import (
    Video,
    Point
)


@receiver(post_save, sender=Video)
def VideoSignals(sender, instance, created, *args, **kwargs):
    if kwargs.get('update_fields') and 'is_verified' in kwargs['update_fields']:
        point_value = 0.1

        if instance.is_verified and instance.verified_at:
            Point.objects.create(
                user=instance.verified_by,
                video=instance,
                point_value=point_value
            )
