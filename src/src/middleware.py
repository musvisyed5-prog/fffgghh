from django.conf import settings
from django.utils import translation

LANGUAGE_SESSION_KEY = "django_language"


class UserLanguageMiddleware:
    """
    Middleware for handling user language preferences and activation.
    This middleware sets the active language for each request based on the following priority:
    1. User's stored language preference (if authenticated)
    2. Language from browser cookie
    3. Language from session
    The middleware also handles saving language preference changes when a user switches
    languages via the UI.
    """
 
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        user = getattr(request, "user", None)
        response = self.get_response(request)

        # Save change if user switched language via UI
        if user and user.is_authenticated:
            cookie_lang = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)

            if cookie_lang and cookie_lang != user.language:
                user.language = cookie_lang
                user.save(update_fields=["language"])

        return response
