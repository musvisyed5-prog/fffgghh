from django.urls import path

from portfolio.views import (
    TalentListView,
    TalentDetailView,
    PortfolioUpdateView,
    AddExperienceView,
    UpdateExperienceView,
    DeleteExperienceView,
    AddLanguageView,
    DeleteLanguageView,
    AddVideoView,
    DeleteVideoView,
    MagicLinkPeekView,
    VerifyMagicLinkView,
    VerifiedWorksView,
    PointView
)

urlpatterns = [
    path('talents/', TalentListView.as_view(), name='talents'),
    path('talent/<int:public_id>/',
         TalentDetailView.as_view(), name='talent_details'),
    path('update/', PortfolioUpdateView.as_view(), name='portfolio_update'),
    path('create-experience/', AddExperienceView.as_view(),
         name='create_experience'),
    path('update-experience/<int:pk>/', UpdateExperienceView.as_view(),
         name='update_experience'),
    path('delete-experience/<int:pk>/', DeleteExperienceView.as_view(),
         name='delete_experience'),
    path('create-language/', AddLanguageView.as_view(), name='create_language'),
    path('delete-language/<int:pk>/', DeleteLanguageView.as_view(), name='delete_language'),
    path('create-video/', AddVideoView.as_view(), name='create_video'),
    path('delete-video/<uuid:pk>/', DeleteVideoView.as_view(), name='delete_video'),
    path('verify-preview/<uuid:pk>/', MagicLinkPeekView.as_view(), name='magic_peek'),
    path('verify/<uuid:pk>/', VerifyMagicLinkView.as_view(), name='magic_link_verify'),
    path('verified-works/', VerifiedWorksView.as_view(), name="verified_work"),
    path('my-points/', PointView.as_view(), name="my_points")
]


app_name = 'portfolio'
