from django.http import JsonResponse
from django.views import View
from django.conf import settings
from django.core.cache import cache
from django.utils.translation import gettext as _

from src.services.ai import rewrite_text


class AIRewriteView(View):
    AI_REWRIE_LIMIT = settings.GROQ_REWRITE_LIMIT
    CACHE_TIMEOUT = settings.GROQ_CACHE_TIMEOUT

    def post(self, request):
        user_key = f"ai_rewrite_{request.user.id}"
        count = cache.get(user_key, 0)


        if count >= self.AI_REWRIE_LIMIT:
            return JsonResponse({
                "error": _("AI rewrite limit reached. Limit will reset after 24 hours."),
                "remaining": 0
            }, status=403)

        text = request.POST.get("text")
 
        if text != "":
            try:
                result = rewrite_text(text)
            except Exception:
                return JsonResponse({
                    "error": _("something went wrong"),
                    "remaining": count
                })
            count += 1
            cache.set(user_key, count, timeout=self.CACHE_TIMEOUT)

            return JsonResponse({
                "result": result,
                "remaining": count
            })
        else:
            return JsonResponse({
                "error": _("Empty text"),
                "remaining": count
            })
