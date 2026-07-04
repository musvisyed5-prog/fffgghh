import django_filters
from django.contrib.auth import get_user_model


User = get_user_model()


class TalentFilter(django_filters.FilterSet):

    class Meta:
        model = User
        fields = {
            "title",
            "type",
            "location",
            "platform",
        }
