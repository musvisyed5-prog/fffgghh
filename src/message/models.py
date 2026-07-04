import random
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Message(models.Model):
    sender = models.ForeignKey(
        User,
        verbose_name=_('sender'),
        on_delete=models.CASCADE,
        related_name='sender_message_related',
        related_query_name='sender_message_query'
    )
    message = models.TextField(
        _("message"),
        null=False,
        blank=False
    )
    date_created = models.DateTimeField(
        _('date created'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _("message")
        verbose_name_plural = _("messages")

    def __str__(self):
        return str(self.id)


class Converstation(models.Model):
    converstation_id = models.IntegerField(
        unique=True,
        editable=False,
    )
    users = models.ManyToManyField(
        User,
        verbose_name=_('users'),
        related_name='users_message_related',
        related_query_name='users_message_query'
    )
    messages = models.ManyToManyField(
        Message,
        verbose_name=_('messages'),
        related_name='message_converstation_related',
        related_query_name='message_converstation_query'
    )
    date_created = models.DateTimeField(
        _('date created'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _("converstation")
        verbose_name_plural = _("converstations")
        ordering = ("-date_created",)

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        if not self.converstation_id:
            self.converstation_id = self.generate_unique_id()
        super().save(*args, **kwargs)

    def generate_unique_id(self):
        while True:
            new_id = random.randint(100000, 999999)  # 6-digit
            if not Converstation.objects.filter(converstation_id=new_id).exists():
                return new_id
