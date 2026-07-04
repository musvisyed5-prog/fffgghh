from django.urls import path

from company.views import (
    CompanyUpsertView,
    CompanyDeListView,
    CompanyView,
)


urlpatterns = [
    path('profile/',
        CompanyUpsertView.as_view(),
        name='company_profile'
    ),
    path('<slug:slug>/', CompanyView.as_view(), name='company_detail'),
    path('<slug:slug>/delete/', CompanyDeListView.as_view(), name='company_delete'),
]

app_name = 'company'