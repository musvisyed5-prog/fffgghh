from django.core.cache import cache
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal
from django.shortcuts import (
    render,
    get_object_or_404,
    redirect
)
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.views.generic import (
    DetailView,
    ListView,
    UpdateView,
    CreateView,
    DeleteView
)
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin
)
from allauth.socialaccount.models import SocialAccount

from portfolio.models import (
    Portfolio,
    Experience,
    Language,
    Video,
    Point,
    BagdesHistory
)
from message.forms import MessageForm
from portfolio.forms import (
    PortfolioUpdatetForm,
    ExperienceForm,
    LanguageForm,
    VideoForm
)
from job.models import JobApplicant
from portfolio.utils import Verification


class TalentListView(ListView):
    model = Portfolio
    fields = '__all__'
    template_name = "talent/list.html"
    context_object_name = "talents"


class TalentDetailView(DetailView):
    model = Portfolio
    fields = '__all__'
    template_name = "talent/details.html"
    context_object_name = "talent"
    pk_url_kwarg = "public_id"

    def get_ai_rewrite_limit_used(self, request, *args, **kwargs):
        """
        Retrieve the current AI rewrite limit usage for the authenticated user.
        This method checks the cache to get the number of times the user has used
        the AI rewrite feature within the current cache period.
        Args:
            request: The HTTP request object containing the authenticated user information.
        Returns:
            int: The number of AI rewrite operations used by the user. Returns 0 if
                 no usage data exists in the cache.
        """

        cache_key = f"ai_rewrite_{request.user.id}"
        ai_rewrite_limit_used = cache.get(cache_key, 0)

        return ai_rewrite_limit_used

    def get_object(self):
        return Portfolio.objects.get(
            public_id=self.kwargs["public_id"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_user = False

        if self.request.user.is_authenticated:
            is_user = self.request.user.public_id == self.get_object().user.public_id

        if self.request.user.groups.filter(name__in=['creator', 'company']).exists() and JobApplicant.objects.filter(
            applicant=self.get_object().user,
            job__recruter=self.request.user
        ).exists():
            context["message_form"] = MessageForm

        if is_user:
            ai_rewrite_limit_used = self.get_ai_rewrite_limit_used(
                self.request)
            context['form'] = PortfolioUpdatetForm(
                instance=self.get_object(),
                ai_rewrite_limit_used=ai_rewrite_limit_used
            )
            context["experience_form"] = ExperienceForm(
                ai_rewrite_limit_used=ai_rewrite_limit_used)
            context["language_form"] = LanguageForm()
            context["video_form"] = VideoForm(
                ai_rewrite_limit_used=ai_rewrite_limit_used)

        context['is_user'] = is_user
        return context


class PortfolioUpdateView(LoginRequiredMixin, UpdateView):
    model = Portfolio
    form_class = PortfolioUpdatetForm

    def get_object(self):
        user = self.request.user
        return Portfolio.objects.get(user=user)

    def get_success_url(self):
        return reverse_lazy("portfolio:talent_details", kwargs={"public_id": self.get_object().public_id})

    def get_login_url(self):
        return reverse_lazy('core:oauth_login', kwargs={'role': 'talent'})


class BaseMixin(LoginRequiredMixin):
    def get_portfolio(self):
        user = self.request.user
        return Portfolio.objects.get(user=user)

    def get_success_url(self):
        return reverse_lazy("portfolio:talent_details", kwargs={"public_id": self.get_portfolio().public_id})
    
    def get_login_url(self):
        return reverse_lazy('core:oauth_login', kwargs={'role': 'talent'})


class AddExperienceView(BaseMixin, CreateView):
    model = Experience
    form_class = ExperienceForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        form = super().form_valid(form)

        portfolio = self.get_portfolio()
        portfolio.experiences.add(self.object)
        return form


class UpdateExperienceView(BaseMixin, UpdateView):
    model = Experience
    form_class = ExperienceForm
    template_name = 'portfolio/experience_update.html'
    context_object_name = 'experience'

    def get_ai_rewrite_limit_used(self, request, *args, **kwargs):
        """
        Retrieve the current AI rewrite limit usage for the authenticated user.
        This method checks the cache to get the number of times the user has used
        the AI rewrite feature within the current cache period.
        Args:
            request: The HTTP request object containing the authenticated user information.
        Returns:
            int: The number of AI rewrite operations used by the user. Returns 0 if
                 no usage data exists in the cache.
        """

        cache_key = f"ai_rewrite_{request.user.id}"
        ai_rewrite_limit_used = cache.get(cache_key, 0)

        return ai_rewrite_limit_used

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['ai_rewrite_limit_used'] = self.get_ai_rewrite_limit_used(
            self.request)

        return kwargs


class DeleteExperienceView(BaseMixin, DeleteView):
    model = Experience


class AddLanguageView(BaseMixin, CreateView):
    model = Language
    form_class = LanguageForm

    def form_valid(self, form):
        form = super().form_valid(form)

        portfolio = self.get_portfolio()
        portfolio.languages.add(self.object)
        return form


class DeleteLanguageView(BaseMixin, DeleteView):
    model = Language


class AddVideoView(BaseMixin, CreateView):
    model = Video
    form_class = VideoForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        form = super().form_valid(form)

        portfolio = self.get_portfolio()
        portfolio.videos.add(self.object)
        return form

    def get_ai_rewrite_limit_used(self, request, *args, **kwargs):
        """
        Retrieve the current AI rewrite limit usage for the authenticated user.
        This method checks the cache to get the number of times the user has used
        the AI rewrite feature within the current cache period.
        Args:
            request: The HTTP request object containing the authenticated user information.
        Returns:
            int: The number of AI rewrite operations used by the user. Returns 0 if
                 no usage data exists in the cache.
        """

        cache_key = f"ai_rewrite_{request.user.id}"
        ai_rewrite_limit_used = cache.get(cache_key, 0)

        return ai_rewrite_limit_used

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['ai_rewrite_limit_used'] = self.get_ai_rewrite_limit_used(
            self.request)
        return kwargs


class DeleteVideoView(BaseMixin, DeleteView):
    model = Video


class MagicLinkPeekView(DetailView):
    model = Video
    template_name = "portfolio/peek.html"
    context_object_name = 'video'


class VerifyMagicLinkView(LoginRequiredMixin, PermissionRequiredMixin, View):
    model = Video
    template_name = "portfolio/peek.html"
    permission_required = 'portfolio.can_verify'

    def get(self, request, *args, **kwargs):
        video = get_object_or_404(Video, pk=kwargs.get('pk'))
        return render(request, self.template_name, {"video": video})

    def post(self, request, *args, **kwargs):
        video = get_object_or_404(Video, pk=kwargs.get('pk'))

        try:
            verification = Verification(
                user=request.user,
                provider=video.platform,
                video=video
            )
            can_verify = verification.process()
            if can_verify:
                video.is_verified = True
                video.verified_by = request.user
                video.verified_at = timezone.now()
                video.save(
                    update_fields=[
                        'is_verified',
                        'verified_by',
                        'verified_at'
                    ]
                )

                BagdesHistory.objects.create(
                    user=video.user,
                    video=video,
                )

                return redirect(reverse_lazy('portfolio:verified_work'))

            else:
                messages.error(request, _("Unable to verify work"))
        except SocialAccount.DoesNotExist:
            messages.info(request, _("Please connect your account first"))
            return redirect(reverse_lazy("socialaccount_connections"))

        return redirect(reverse_lazy('portfolio:magic_peek', kwargs={'pk': kwargs.get('pk')}))
    

    def get_login_url(self):
        return reverse_lazy('core:oauth_login', kwargs={'role': 'creator'})


class VerifiedWorksView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'portfolio.can_view_verified_work'
    model = Video
    template_name = 'portfolio/verified.html'
    context_object_name = 'works'

    def get_queryset(self):
        return super().get_queryset().filter(verified_by=self.request.user)


class PointView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'portfolio.view_point'
    model = Point
    fields = [
        'point_value',
        'date_expire',
        'is_redeemed'
    ]
    template_name = 'portfolio/point.html'
    context_object_name = 'points'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = context['points']

        now = timezone.now()

        total_points = qs.aggregate(total=Sum('point_value'))['total'] or 0

        active_points_qs = qs.filter(
            is_redeemed=False,
            date_expire__gt=now
        )
        active_points = active_points_qs.aggregate(
            total=Sum('point_value'))['total'] or 0

        context.update({
            'total_points': total_points,
            'total_value': total_points * Decimal("0.1"),  # or apply conversion logic
            'active_points': active_points,
            'active_value': active_points * Decimal("0.1"),
        })

        return context
