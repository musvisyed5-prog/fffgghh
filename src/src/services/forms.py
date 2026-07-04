from django import forms
from django.conf import settings
from django.utils.translation import gettext as _

AI_REWRITE_LIMIT = settings.GROQ_REWRITE_LIMIT

class AITextarea(forms.Textarea):

    template_name = "services/ai_textarea.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        context["widget"]["ai_rewrite_limit_used"] = getattr(
            self, "ai_rewrite_limit_used", 0
        )
        context["widget"]["ai_rewrite_limit"] = AI_REWRITE_LIMIT

        return context