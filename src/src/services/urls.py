from django.urls import path

from src.services.views import (
    AIRewriteView
)

urlpatterns = [
    path("rewrite/", AIRewriteView.as_view(), name="ai_rewrite")
]


app_name = 'ai'