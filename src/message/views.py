from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView
)
from django.shortcuts import (
    get_object_or_404,
    redirect
)
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy

from core.utils import get_url
from message.forms import MessageForm
from message.models import (
    Converstation,
    Message
)
from message.emails import SENDCONVERSTATIONEMAIL

User = get_user_model()


class MessageListView(LoginRequiredMixin, ListView):
    model = Converstation
    field = "__all__"
    template_name = "list.html"
    context_object_name = 'converstations'

    def get_queryset(self):
        return super().get_queryset().filter(users=self.request.user)


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Converstation
    field = "__all__"
    template_name = "detail.html"
    context_object_name = 'converstation'
    pk_url_kwarg = "converstation_id"

    def get_object(self):
        return get_object_or_404(Converstation,  converstation_id=self.kwargs["converstation_id"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['converstations'] = Converstation.objects.filter(
            users=self.request.user
        )
        context['reciever'] = self.get_object().users.exclude(id=self.request.user.pk).first()
        return context



class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    converstation_id = None

    def form_valid(self, form):
        sender = self.request.user
        public_id = self.kwargs.get("public_id")

        receiver = get_object_or_404(User, public_id=public_id)

        # 🔍 Find existing conversation
        conversation = (
            Converstation.objects
            .filter(users=sender)
            .filter(users=receiver)
            .first()
        )

        # 🆕 Create if not exists
        if not conversation:
            conversation = Converstation.objects.create()
            conversation.users.add(sender, receiver)

        message = form.save(commit=False)
        message.sender = sender
        message.save()

        conversation.messages.add(message)
        self.converstation_id = conversation.converstation_id
        url = get_url(self.request)
        SENDCONVERSTATIONEMAIL.enqueue(
            url,
            form.instance.pk,
            receiver.pk,
            conversation.converstation_id,
        )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("message:message_detail", kwargs={"converstation_id": self.converstation_id})
