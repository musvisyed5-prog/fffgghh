from django.views.generic import (
    DetailView,
    DeleteView
)
from django.core.cache import cache
from django.contrib import messages
from django.shortcuts import render
from django.views import View
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin
)

from company.forms import (
    CompanyUpdateAndRegistationForm,
)
from company.models import (
    PhoneNumber,
    Company
)


class CompanyUpsertView(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "company_upsert.html"
    form_class = CompanyUpdateAndRegistationForm
    success_url = reverse_lazy("company:company_profile")

    def get_user(self):
        """
        Retrieve the user object from the current request.
        Attempts to get the 'user' attribute from the request object.
        If the attribute does not exist, returns None.
        Returns:
            User: The authenticated user object from the request, or None if not available.
        """

        return getattr(self.request, 'user', None)

    def get_company(self):
        """
        Retrieve the company associated with the current user.
        This method fetches the user object and returns the related company
        through the 'user_company_related' relationship attribute.
        Returns:
            Company or None: The company object related to the current user,
                            or None if no related company exists.
        """

        user = self.get_user()
        return getattr(user, 'user_company_related', None)

    def has_permission(self):
        user = self.request.user
        company = self.get_company()

        if not user.has_perm('company.view_company'):
            return False

        if company:
            return user.has_perm('company.change_company')
        else:
            return user.has_perm('company.add_company')
        
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


    def get(self, request):
        company = self.get_company()
        ai_rewrite_limit_used = self.get_ai_rewrite_limit_used(request)
        form = self.form_class(instance=company, ai_rewrite_limit_used=ai_rewrite_limit_used)

        if company and company.phone:
            form.initial["code"] = company.phone.code
            form.initial["number"] = company.phone.number

        context = {
            "form": form,
            "company": company,
            "is_listed": getattr(company, 'is_listed',  False)
        }
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        company = self.get_company()
        ai_rewrite_limit_used = self.get_ai_rewrite_limit_used(request)
        form = self.form_class(request.POST, instance=company, ai_rewrite_limit_used=ai_rewrite_limit_used)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user

            code = form.cleaned_data["code"]
            number = form.cleaned_data["number"]

            if instance.phone:
                instance.phone.code = code
                instance.phone.number = number
                instance.phone.save()
                messages.success(
                    request, 
                    _("your company profile has been updated.")
                )
            else:
                instance.phone = PhoneNumber.objects.create(
                    code=code, number=number
                )
                messages.success(request, _("company profile created"))

            instance.save()
            return redirect(self.success_url)

        return render(request, self.template_name, {"form": form})


class CompanyView(DetailView):
    model = Company
    template_name = 'company_detail.html'
    context_object_name = 'company'

    def get_queryset(self):
        return super().get_queryset().filter(is_listed=True).select_related(
            'user', 'phone'
        )


class CompanyDeListView(PermissionRequiredMixin, DeleteView):
    model = Company
    permission_required = [
        'company.view_company',
        'company.delete_company',
    ]
    template_name = 'company_delist.html'
    success_url = reverse_lazy('company:company_profile')

    def post(self, request, *args, **kwargs):
        object = self.get_object()
        object.is_listed = False
        object.save(update_fields=['is_listed','date_updated'])

        messages.info(request, _("company delist to relist contact support"))
        return redirect(self.success_url)