from core.utils import BaseEmailServices
from django.urls import reverse
from django_tasks import task
from message.models import Message
from django.contrib.auth import get_user_model

EmailService = BaseEmailServices()


User = get_user_model()

@task()
def SENDCONVERSTATIONEMAIL(    
    url,
    message_id,
    receiver_id,
    converstation_id
):
    message = Message.objects.get(pk=message_id)
    receiver = User.objects.get(pk=receiver_id)

    sender = message.sender
    
    subject = f"New message from {sender.first_name}"
    base_url = url

    conversation_url = f"{base_url}{reverse('message:message_detail', kwargs={"converstation_id": converstation_id})}"

    context = {
        "receiver_name": f"{receiver.first_name} {receiver.last_name}",
        "conversation_url": conversation_url,
    }

    EmailService.send(
        template="email/new_message.html",
        context=context,
        subject=subject,
        recipients=[receiver.email],
    )
