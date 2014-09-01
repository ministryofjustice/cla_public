from datetime import timedelta
from django.contrib.auth import logout
from django.utils.datetime_safe import datetime
from session_security.middleware import SessionSecurityMiddleware
from session_security.settings import EXPIRE_AFTER, PASSIVE_URLS
from session_security.utils import get_last_activity, set_last_activity


class AnonymousUserSessionSecurityMiddleware(SessionSecurityMiddleware):

    def process_request(self, request):
        """ Update last activity time or logout. """
        now = datetime.now()
        self.update_last_activity(request, now)

        delta = now - get_last_activity(request.session)
        if delta >= timedelta(seconds=EXPIRE_AFTER):
            logout(request)
        elif request.path not in PASSIVE_URLS:
            set_last_activity(request.session, now)

