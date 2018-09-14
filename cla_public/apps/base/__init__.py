"Base app"
import datetime
from flask import Blueprint, after_this_request, request

base = Blueprint('base', __name__)

@base.before_app_request
def detect_user_locale():
    locale = request.args.get('locale')
    
    if locale is not None:
        @after_this_request
        def remember_locale(response):
            expires = datetime.datetime.now() + datetime.timedelta(days=30)
            response.set_cookie('locale', locale, expires=expires)
            return response
