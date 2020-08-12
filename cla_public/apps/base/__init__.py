"Base app"
import urllib
import datetime
from flask import Blueprint, after_this_request, request, redirect, current_app

base = Blueprint("base", __name__)


@base.before_app_request
def detect_user_locale():
    request_args = request.args.to_dict()
    locale = request_args.pop("locale", None)

    if locale is not None:

        @after_this_request
        def remember_locale(response):
            expires = datetime.datetime.now() + datetime.timedelta(days=30)
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
        return redirect("/start")
