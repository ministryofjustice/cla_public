# coding: utf-8
"CLA Public app"

import logging
import logging.config
import os

from flask import Flask, render_template, session
from flask_talisman import Talisman
from flask.ext.babel import Babel
from flask.ext.cache import Cache
from flask.ext.mail import Mail
import urllib3.contrib.pyopenssl
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from cla_public.django_to_jinja import change_jinja_templates
from cla_public.apps.geocoder.views import geocoder
from cla_public.apps.base.views import base
from cla_public.apps.contact.views import contact
from cla_public.apps.checker.views import checker
from cla_public.apps.scope.urls import scope
from cla_public.apps.checker.session import CheckerSessionInterface, CustomJSONEncoder
from cla_public.libs import honeypot
from cla_public.libs.utils import get_locale


sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"), environment=os.environ.get("CLA_ENV"), integrations=[FlaskIntegration()]
)


def create_app(config_file=None):
    app = Flask(__name__)
    # Adds security to Flask, unsafe eval is required to use the webpack
    csp = {
        "default-src": ["'self'", "*.googletagmanager.com"],
        "img-src": [
            "'self'",
            "*.googleapis.com",
            "*.gstatic.com",
            "*.google.com",
            "*.googleusercontent.com",
            "data:",
            "*.googletagmanager.com",
            "*.analytics.google.com",
            "*.google.co.uk",
            "*.g.doubleclick.net",
            "*.google-analytics.com",
        ],
        "object-src": "'self'",
        "script-src": [
            "'unsafe-eval'",
            "'self'",
            "*.googleapis.com",
            "*.gstatic.com",
            "*.google.com",
            "*.ggpht.com",
            "*.googleusercontent.com",
            "blob:",
            "ajax.aspnetcdn.com",
            "*.googletagmanager.com",
            "*.analytics.google.com",
            "*.g.doubleclick.net",
            "*.google.co.uk",
            "*.google-analytics.com",
        ],
        "frame-src": ["'self'", "*.google.com"],
        "connect-src": [
            "'self'",
            "*.googleapis.com",
            "*.google.com",
            "*.gstatic.com",
            "data:",
            "blob:",
            "*.google-analytics.com",
            "*.analytics.google.com",
            "*.googletagmanager.com",
            "*.g.doubleclick.net",
            "*.google.co.uk",
        ],
        "font-src": ["'self'", "data:", "fonts.gstatic.com"],
        "style-src": [
            "'self'",
            "'unsafe-inline'",
            "*.googleapis.com",
            "*.google.com",
            "*.google.co.uk",
            "fonts.googleapis.com",
            "*.gstatic.com",
        ],
        "worker-src": "blob:",
    }
    if os.environ.get("CIRCLE_BUILD_NUM"):
        Talisman(
            app,
            force_https=False,
            content_security_policy=None,
            x_content_type_options=False,
            session_cookie_secure=False,
            session_cookie_http_only=False,
        )
    elif os.environ.get("DOCKER_BUILDKIT") == 1 or os.environ.get("TESTING") == "True":
        Talisman(
            app,
            content_security_policy=csp,
            content_security_policy_nonce_in=["script-src"],
            x_content_type_options=False,
            force_https=False,
            session_cookie_secure=False,
            session_cookie_http_only=False,
        )
    else:
        Talisman(
            app,
            content_security_policy=csp,
            content_security_policy_nonce_in=["script-src"],
            x_content_type_options=False,
        )
    app = change_jinja_templates(app)
    if config_file:
        app.config.from_pyfile(config_file)
    else:
        app.config.from_envvar("CLA_PUBLIC_CONFIG")

    app.babel = Babel(app)
    app.babel.localeselector(get_locale)

    app.cache = Cache(app)

    app.mail = Mail(app)

    for extension in app.config["EXTENSIONS"]:
        extension.init_app(app)

    app.session_interface = CheckerSessionInterface()
    app.json_encoder = CustomJSONEncoder

    register_error_handlers(app)

    app.add_template_global(honeypot.FIELD_NAME, name="honeypot_field_name")

    def put_GTM_ANON_ID_to_templates():
        GTM_ANON_ID = session.get("GTM_ANON_ID", "")
        return {"GTM_ANON_ID": GTM_ANON_ID}

    base.context_processor(put_GTM_ANON_ID_to_templates)
    scope.context_processor(put_GTM_ANON_ID_to_templates)
    checker.context_processor(put_GTM_ANON_ID_to_templates)
    contact.context_processor(put_GTM_ANON_ID_to_templates)

    app.register_blueprint(base)
    app.register_blueprint(geocoder)
    app.register_blueprint(contact)
    app.register_blueprint(scope)
    if not app.config.get("CONTACT_ONLY"):
        app.register_blueprint(checker)

    logging.config.dictConfig(app.config["LOGGING"])
    # quiet markdown module
    logging.getLogger("MARKDOWN").setLevel(logging.WARNING)

    if app.debug:
        from werkzeug.debug import DebuggedApplication

        app.wsgi_app = DebuggedApplication(app.wsgi_app, True)

    return app


def register_error_handlers(app):
    """
    Assign error page templates to all error status codes we care about
    """

    error_handlers = {
        "404.html": [404],
        "4xx.html": [400, 401, 402, 403, 405, 406, 407, 408, 409, 414, 429],
        "5xx.html": [500, 501, 502, 503, 504, 505],
    }

    def make_handler(code, template):
        def handler(e):
            return render_template(os.path.join("errors", template), code=code), code

        return handler

    for template, codes in error_handlers.iteritems():
        for code in codes:
            app.register_error_handler(code, make_handler(code, template))

    return app


urllib3.contrib.pyopenssl.inject_into_urllib3()
