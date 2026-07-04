from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import (
    redirect,
    render
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin


from job.utils import get_dashboard_anylatics


class HomView(TemplateView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse_lazy('dashboard'))

        return super().get(request, *args, **kwargs)



class DashboardView(LoginRequiredMixin, View):
    template_name = 'pages/dashboard.html'

    def get(self, request, *args, **kwargs):
        context = get_dashboard_anylatics(user=request.user)
        return render(request, self.template_name, context=context)