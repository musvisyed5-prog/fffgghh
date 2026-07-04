from django.contrib import admin

from message.models import (
    Message,
    Converstation
)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    pass


@admin.register(Converstation)
class ConverstationAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'converstation_id',
        'date_created'
    ]
    filter_horizontal = [
        'users'
    ]
