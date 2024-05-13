"Base app"
import urllib
from datetime import datetime, timedelta
import re
import uuid
from flask import Blueprint, after_this_request, request, redirect, current_app, session

base = Blueprint("base", __name__)


@base.before_app_request
def detect_user_locale():
    request_args = request.args.to_dict()
    locale = request_args.pop("locale", None)

    if locale is not None:

        @after_this_request
        def remember_locale(response):
            expires = datetime.now() + timedelta(days=30)
            path = request.path
            if request_args:
                path = "%s?%s" % (path, urllib.urlencode(request_args))
            response = redirect(path)
            response.set_cookie("locale", locale, expires=expires)
            return response


@base.before_app_request
def detect_maintenance():
    maintenance_mode = current_app.config.get("MAINTENANCE_MODE", False)
    if maintenance_mode and request.path != u"/maintenance":
        return redirect("/maintenance")
    if not maintenance_mode and request.path == u"/maintenance":
        return redirect("/")


def get_GTM_ANON_ID_from_cookie():
    UUID_PATTERN = re.compile(r"^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$")
    anon_id_cookie = request.cookies.get("GTM_ANON_ID")
    if anon_id_cookie is None or not UUID_PATTERN.match(anon_id_cookie):
        return None
    return anon_id_cookie


@base.before_app_request
def detect_GTM_ANON_ID():
    # The variable is used to track user anonymously across services for Google Tag Manager
    if "GTM_ANON_ID" not in session:
        anon_id_cookie = get_GTM_ANON_ID_from_cookie()
        if anon_id_cookie:
            session["GTM_ANON_ID"] = anon_id_cookie
        else:

            @after_this_request
            def remember_GTM_ANON_ID(response):
                session["GTM_ANON_ID"] = str(uuid.uuid4())
                expiration_date = datetime.utcnow() + timedelta(days=30)
                path = request.path
                response = redirect(path)
                response.set_cookie("GTM_ANON_ID", session.get("GTM_ANON_ID"), expires=expiration_date)
                return response
