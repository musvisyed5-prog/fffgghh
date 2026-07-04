from django.urls import path
from django.views.generic import TemplateView

from core.views import (
    SocialLoginView,
    ProfileView,
    AccountSuspendView,
    NotificationView,
    FeedbackView,
    ReportView,
    DevLoginAsView
)

urlpatterns = [
    path('oauth/<str:role>/', SocialLoginView.as_view(), name='oauth_login'),
    path('dev-login-as/', DevLoginAsView.as_view(), name='dev_login_as'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('settings/', AccountSuspendView.as_view(), name='deactive'),
    path('notifications/', NotificationView.as_view(), name='notifications'),
    path('feedback/', FeedbackView.as_view(), name='feedback'),
    path('report/', ReportView.as_view(), name='report'),
    path('done/', TemplateView.as_view(template_name='done.html'), name='done')
]

app_name = 'core'
                                          