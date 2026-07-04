from django.urls import path

from job.views import (
    JobListView,
    JobCreateView,
    JobDetailView,
    JobUpdateView,
    JobDeleteView,
    OwnedJobListView,
    CustomQuestionListView,
    CustomQuestionCreateView,
    CustomQuestionUpdateView,
    JobApplicantListView,
    OwnedJobApplications,
    JobApplicantCreateView,
    JobApplicantUpdateView
)


urlpatterns = [
    path('', JobListView.as_view(), name='job_list'),
    path('<uuid:pk>/', JobDetailView.as_view(), name='job_detail'),
    path('new/', JobCreateView.as_view(), name='job_create'),
    path('<uuid:pk>/update/', JobUpdateView.as_view(), name='job_update'),
    path('<uuid:pk>/delete/', JobDeleteView.as_view(), name='job_delete'),
    path('me/', OwnedJobListView.as_view(), name='owned_jobs'),
    path(
        '<uuid:pk>/custom-questions/',
        CustomQuestionListView.as_view(),
        name="custom_question_list"
    ),

    path(
        '<uuid:pk>/custom-question/new/',
        CustomQuestionCreateView.as_view(),
        name='custom_question_create'
    ),
    path(
        '<uuid:job_id>/custom-question/update/',
        CustomQuestionUpdateView.as_view(),
        name='custom_question_update'
    ),
    path(
        '<uuid:pk>/applicants/',
        JobApplicantListView.as_view(),
        name="jobapplicant_list"
    ),
    path(
        'applications',
        OwnedJobApplications.as_view(),
        name="owned_applications"
    ),
    path(
        '<uuid:pk>/apply/',
        JobApplicantCreateView.as_view(),
        name="jobapplicant_create"
    ),
    path(
        '<uuid:job_id>/applicant/<uuid:pk>/',
        JobApplicantUpdateView.as_view(),
        name="jobapplicant_update"
    ),

]

app_name = 'job'
