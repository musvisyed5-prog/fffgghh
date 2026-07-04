from django.urls import path

from message.views import (
    MessageListView,
    MessageDetailView,
    MessageCreateView
)

urlpatterns = [
    path('', MessageListView.as_view(), name='message_list'),
    path('<int:converstation_id>/', MessageDetailView.as_view(), name='message_detail'),
    path('create/<int:public_id>/', MessageCreateView.as_view(), name='message_create')
]


app_name = 'message'