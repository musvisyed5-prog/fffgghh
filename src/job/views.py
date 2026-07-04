from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.db.models import Q
from django.views import View
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin
)
from django.core.cache import cache
from django.shortcuts import (
    get_object_or_404,
    render
)
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django_filters.views import FilterView

from core.utils import get_url
from job.models import (
    JobPosting,
    CustomQuestion,
    JobApplicant
)
from job.forms import JobPostingForm
from job.filters import (
    JobPostingFilter,
    JobApplicationFilter,
    JobApplicantFilter
)
from job.emails import (
    JOBFILLINGEMAIL,
    JOBSTATUSEMAIL,
    JOBCLOSEDEMAILTOAPPLICANTS
)


class JobListView(FilterView):
    model = JobPosting
    template_name = 'jobposting/list.html'
    context_object_name = 'jobs'
    view_action = 'public-list'
    filterset_class = JobPostingFilter
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.view_action == 'public-list':
            queryset = queryset.filter(is_active=True).filter(
                Q(company__isnull=True) | Q(company__is_listed=True)
            )
        return queryset


class JobDetailView(DetailView):
    model = JobPosting
    template_name = 'jobposting/detail.html'
    context_object_name = 'job'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["application"] = None

        if self.request.user.is_authenticated:
            try:
                application = JobApplicant.objects.get(
                    applicant=self.request.user,
                    job=self.get_object()
                )
                context["application"] = application
            except:
                pass

        return context


class JobCreateUpdateMixin(LoginRequiredMixin, PermissionRequiredMixin):
    model = JobPosting
    form_class = JobPostingForm
    permission_required = None
    template_name = 'jobposting/upsert.html'
    context_action = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        if self.context_action == 'create':
            return reverse_lazy('job:custom_question_create', kwargs={'pk': self.object.pk})
        return self.request.path

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        cache_key = f"ai_rewrite_{self.request.user.id}"
        ai_rewrite_limit_used = cache.get(cache_key, 0)
        kwargs["ai_rewrite_limit_used"] = ai_rewrite_limit_used
        kwargs["user"] = self.request.user
        return kwargs


class JobCreateView(JobCreateUpdateMixin, CreateView):
    permission_required = 'job.add_jobposting'
    context_action = 'create'

    def form_valid(self, form):
        user = self.request.user
        form.instance.recruter = user

        if user.groups.filter(name='company').exists():
            company = getattr(user, "user_company_related", None)

            if not company:
                messages.error(
                    self.request,
                    _("complete your company profile to post a job")
                )
                return redirect("company:company_profile")
            form.instance.company = company
        messages.success(
            self.request,
            _("Job posted successfully")
        )
        return super().form_valid(form)


class JobUpdateView(JobCreateUpdateMixin, UpdateView):
    model = JobPosting
    permission_required = 'job.change_jobposting'
    context_object_name = 'job'
    context_action = 'update'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _("Job updated successfully."))
        return response


class JobDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = JobPosting
    success_url = reverse_lazy('job:job_list')
    permission_required = 'job.delete_jobposting'

    def post(self, request, *args, **kwargs):
        object = self.get_object()
        object.is_active = False
        object.save(update_fields=['is_active', 'date_updated'])
        url = get_url(request)
        JOBCLOSEDEMAILTOAPPLICANTS.enqueue(url, str(object.pk))
        messages.success(self.request, _("Job deleted successfully."))
        return redirect(self.success_url)


class OwnedJobListView(PermissionRequiredMixin, JobListView):
    permission_required = 'job.view_jobposting'
    template_name = 'jobposting/owned_list.html'
    view_action = 'private-list'

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if user.groups.filter(name="company").exists():
            if not hasattr(user, "user_company_related"): 
                messages.warning(
                    request,
                    _("Create company profile first, then you can post a job.")
                )
                return redirect("company:company_profile")

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(recruter=self.request.user)
        return queryset


class CustomQuestionListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'job.view_customquestion'
    model = CustomQuestion
    template_name = 'customquestion/list.html'
    context_object_name = 'questions'

    def get_queryset(self):
        job_id = self.kwargs.get("pk")
        job = JobPosting.objects.get(pk=job_id)
        return super().get_queryset().filter(job=job)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["job_id"] = self.kwargs.get("pk")
        return context


class CustomQuestionCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = CustomQuestion
    fields = ["structure"]
    permission_required = 'job.add_customquestion'
    template_name = 'customquestion/create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["job_id"] = self.kwargs["pk"]
        return context

    def get_success_url(self):
        return reverse_lazy('job:custom_question_list', kwargs={'pk': self.kwargs["pk"]})

    def form_valid(self, form):
        job = get_object_or_404(JobPosting, pk=self.kwargs["pk"])
        form.instance.job = job
        messages.success(self.request, _("Screening question added successfully."))
        return super().form_valid(form)


class CustomQuestionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = CustomQuestion
    fields = ["structure"]
    permission_required = 'job.change_customquestion'
    template_name = 'customquestion/update.html'

    def get_object(self):
        return CustomQuestion.objects.get(job=self.kwargs['job_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["job_id"] = self.kwargs["job_id"]
        return context
    
    def form_valid(self, form):
        messages.success(self.request, _("Screening question updated successfully."))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('job:custom_question_list', kwargs={'pk': self.kwargs["job_id"]})


class JobApplicantListView(LoginRequiredMixin, PermissionRequiredMixin, FilterView):
    model = JobApplicant
    permission_required = 'job.view_jobapplicant'
    context_object_name = 'applications'
    template_name = 'applicant/list.html'
    view_action = 'recruter-list'
    filterset_class = JobApplicantFilter

    def get_job(self):
        job = None
        try:
            job = JobPosting.objects.get(pk=self.kwargs['pk'])
        except:
            pass
        return job

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.view_action == 'recruter-list':
            job = self.get_job()
            queryset = queryset.filter(job=job)
        else:
            queryset = queryset.filter(applicant=self.request.user)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['job'] = self.get_job()
        return context


class OwnedJobApplications(JobApplicantListView):
    view_action = 'private-list'
    template_name = 'applicant/owned.html'
    permission_required = [
        'job.view_jobapplicant',
        'job.add_jobapplicant'
    ]
    filterset_class = JobApplicationFilter


class JobApplicantCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'job.add_jobapplicant'
    template_name = 'applicant/create.html'
    success_url = reverse_lazy('job:owned_applications')

    def get_job(self):
        job_id = self.kwargs['pk']
        job = JobPosting.objects.get(pk=job_id)
        return job

    def get_context(self):
        job = self.get_job()
        context = {
            "questions": None,
            "job": job
        }
        try:
            context['questions'] = job.job_customquestion_related.structure
        except:
            pass

        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, context=self.get_context())

    def post(self, request, *args, **kwargs):
        job = self.get_job()
        has_applied = JobApplicant.objects.filter(
            job=job, applicant=self.request.user).exists()

        if not has_applied:
            data = request.POST.dict()
            data.pop("csrfmiddlewaretoken", None)
            instance = JobApplicant.objects.create(
                job=job,
                applicant=request.user,
                answer=data
            )
            url = get_url(request)
            JOBFILLINGEMAIL.enqueue(url, str(instance.pk))
            messages.success(request, _("Application sent successfully"))
        else:
            messages.info(request, _(
                "You have already applied for this position"))
        return redirect(reverse_lazy('job:owned_applications'))


class JobApplicantUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'job.change_jobapplicant'
    model = JobApplicant
    fields = [
        'status',
        'status_reason'
    ]
    template_name = 'applicant/update.html'
    context_object_name='application'

    def form_valid(self, form):
        url = get_url(self.request)
        JOBSTATUSEMAIL.enqueue(url, str(self.object.pk))
        messages.success(self.request, _("Application job status updated successfully."))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("job:jobapplicant_list", kwargs={'pk': self.kwargs["job_id"]})
