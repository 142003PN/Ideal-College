from django.utils import timezone
from django.conf import settings
from django.contrib.auth import logout
import datetime


class AutoLogoutMiddleware:
    """
    Logs out users after 10 minutes of true inactivity..
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated:
            timeout = getattr(settings, "AUTO_LOGOUT_TIMEOUT", 600)  # 10 min default

            last_activity = request.session.get("last_activity")

            if last_activity:
                last_activity = datetime.datetime.fromisoformat(last_activity)

                # Check elapsed time
                if (timezone.now() - last_activity).total_seconds() > timeout:
                    logout(request)
                    request.session.flush()

            # Update last activity on EVERY request
            request.session["last_activity"] = timezone.now().isoformat()

        return self.get_response(request)
