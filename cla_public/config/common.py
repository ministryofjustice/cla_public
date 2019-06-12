import os
import datetime

from flask.ext.babel import lazy_gettext as _

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

DEBUG = False

TESTING = False

CLEAR_SESSION = True

GOV_UK_START_PAGE = "https://www.gov.uk/check-legal-aid"

BACKEND_BASE_URI = os.environ.get("BACKEND_BASE_URI", "http://127.0.0.1:8000")  # For healthcheck.json requests

# Disable eligibility check and allow users to request a callback only
CONTACT_ONLY = os.environ.get("CALLMEBACK_ONLY", False) == "True"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": ("%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d " "%(message)s")},
        "simple": {"format": "%(levelname)s %(message)s"},
        "logstash": {"()": "logstash_formatter.LogstashFormatter"},
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        }
    },
    "loggers": {"": {"handlers": ["console"], "level": "DEBUG"}},
}

SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(24))

# Should be True when served over HTTPS, False otherwise (or CSRF will break)
SESSION_COOKIE_SECURE = True

PERMANENT_SESSION_LIFETIME = datetime.timedelta(minutes=5)

APP_SETTINGS = {
    "app_title": _("Check if you can get legal aid"),
    "proposition_title": _("Check if you can get legal aid"),
}

# Timeout for api get requests so they don't hang waiting for a response
API_CLIENT_TIMEOUT = 10

BACKEND_API = {"url": "{url}/checker/api/v1/".format(url=BACKEND_BASE_URI)}

SENTRY_DSN = os.environ.get("RAVEN_CONFIG_DSN", "")
SENTRY_SITE_NAME = os.environ.get("RAVEN_CONFIG_SITE", "")

POSTCODEINFO_API = {
    "auth_token": os.environ.get("POSTCODEINFO_API_TOKEN"),
    "api_url": os.environ.get("POSTCODEINFO_API_URL"),
    "timeout": os.environ.get("POSTCODEINFO_API_TIMEOUT"),
}

OS_PLACES_API_KEY = os.environ.get("OS_PLACES_API_KEY")

ZENDESK_API_USERNAME = os.environ.get("ZENDESK_API_USERNAME")
ZENDESK_API_TOKEN = os.environ.get("ZENDESK_API_TOKEN")
ZENDESK_DEFAULT_REQUESTER = 649762516  # anonymous feedback <noreply@ministryofjustice.zendesk.com>

GA_ID = os.environ.get("GA_ID")

CACHE_TYPE = "simple"

EXTENSIONS = []

CLA_ENV = os.environ.get("CLA_ENV", "dev")

LANGUAGES = [("en", "English"), ("cy", "Welsh")]


def config_path(x):
    return os.path.join(PROJECT_ROOT, "config", "forms", x, "forms_config.yml")


FORM_CONFIG_TRANSLATIONS = {l: config_path(l) for l, label in LANGUAGES}

OPERATOR_HOURS = {
    "weekday": (datetime.time(9, 0), datetime.time(20, 0)),
    "saturday": (datetime.time(9, 0), datetime.time(12, 30)),
    "2018-12-24": (datetime.time(9, 0), datetime.time(17, 30)),
    "2018-12-31": (datetime.time(9, 0), datetime.time(17, 30)),
}

TIMEZONE = "Europe/London"

LAALAA_API_HOST = os.environ.get("LAALAA_API_HOST", "https://prod.laalaa.dsd.io")

MAIL_SERVER = os.environ.get("SMTP_HOST")
MAIL_PORT = os.environ.get("SMTP_PORT", 465)
MAIL_USE_TLS = False
MAIL_USE_SSL = True

MAIL_USERNAME = os.environ.get("SMTP_USER")
MAIL_PASSWORD = os.environ.get("SMTP_PASSWORD")

MAIL_DEFAULT_SENDER = ("Civil Legal Advice", "no-reply@civillegaladvice.service.gov.uk")

# local.py overrides all the common settings.
try:
    from cla_public.config.local import *  # noqa: F401,F403
except ImportError:
    pass
