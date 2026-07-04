from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from django.views import View
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.urls import (
    reverse_lazy,
    reverse
)
from django.contrib.auth import logout
from django.views.generic import (
    UpdateView,
    ListView,
    View as GenericView,
    CreateView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from allauth.socialaccount.adapter import get_adapter as get_social_adapter
from django.conf import settings
from django.http import Http404
from django.contrib.auth import login as auth_login


from core.models import (
    Notification,
    Feedback,
    Report
)

User = get_user_model()


class DevLoginAsView(GenericView):
    """
    DEBUG-only helper: pick any existing user and log in as them instantly.
    Talent/creator accounts are Google-OAuth-only in production, so this is
    the only way to preview their dashboards without real OAuth credentials.
    404s outright unless DEBUG=True.
    """
    template_name = 'dev_login_as.html'

    def dispatch(self, request, *args, **kwargs):
        if not settings.DEBUG:
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        users = User.objects.all().prefetch_related('groups').order_by('id')
        return render(request, self.template_name, {"users": users})

    def post(self, request, *args, **kwargs):
        user_id = request.POST.get('user_id')
        user = User.objects.get(pk=user_id)
        auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('dashboard')


class SocialLoginView(View):
    VALID_ROLES = {'talent', 'creator'}

    def get(self, request, *args, **kwargs):
        role = kwargs.get("role", "").lower()
        next = request.GET.get('next')

        if role not in self.VALID_ROLES:
            messages.error(request, _("invalid authentication request"))
            return redirect("home")

        if not get_social_adapter(request).list_apps(request, provider="google"):
            messages.error(
                request,
                _("Google sign-in isn't configured yet. Please check back soon.")
            )
            return redirect("home")

        request.session["group"] = role
        request.session["next"] = next
        request.session.modified = True

        return redirect(reverse('google_login'))


class ProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'profile.html'
    context_object_name = 'user'
    model = User
    fields = [
        'first_name',
        'last_name'
    ]

    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, _("Profile updated Successfully"))
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('core:profile')


class AccountSuspendView(LoginRequiredMixin, GenericView):
    model = User
    success_url = reverse_lazy("home")
    template_name = "settings.html"

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save(update_fields=["is_active"])
        messages.success(request, _("account deactivated"))
        messages.info(request, _("logging out ......"))
        logout(request)
        return redirect(reverse_lazy('home'))


class NotificationView(LoginRequiredMixin, ListView):
    model = Notification
    fields = "__all__"
    template_name = 'notifications.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        one_week_ago = timezone.now() - timedelta(days=7)

        return Notification.objects.filter(
            Q(recipient=self.request.user) | Q(recipient__isnull=True),
            date_created__gte=one_week_ago
        ).order_by("-date_created")

class FeedbackView(LoginRequiredMixin, CreateView):
    model = Feedback
    fields = [
        'subject',
        'category',
        'desc'
    ]
    template_name = "feedback.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("core:done")


class ReportView(LoginRequiredMixin, CreateView):
    model = Report
    fields = [
        'reason',
        'desc'
    ]
    template_name = "report.html"

    def form_valid(self, form):
        form.instance.reporter = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("core:done")
