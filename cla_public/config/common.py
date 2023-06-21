import os
import datetime

from flask.ext.babel import lazy_gettext as _
from cla_common.services import CacheAdapter, TranslationAdapter

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

DEBUG = False

# Sets whether the emergency message displays on the contact page or not
EMERGENCY_MESSAGE_ON = os.environ.get("EMERGENCY_MESSAGE_ON", "False") == "True"
EMERGENCY_MESSAGE_TITLE = os.environ.get("EMERGENCY_MESSAGE_TITLE", "Title not set")
EMERGENCY_MESSAGE_TEXT = os.environ.get("EMERGENCY_MESSAGE_TEXT", "Text not set")

# Sets whether the updated family issue text displays on the outcome (/result/eligible or /result/provisional) pages or not
FAMILY_ISSUE_FEATURE_FLAG = os.environ.get("FAMILY_ISSUE_FEATURE_FLAG", "False") == "True"

TESTING = os.environ.get("TESTING", "False").upper() == "TRUE"

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

POSTCODEINFO_API = {
    "auth_token": os.environ.get("POSTCODEINFO_API_TOKEN"),
    "api_url": os.environ.get("POSTCODEINFO_API_URL"),
    "timeout": os.environ.get("POSTCODEINFO_API_TIMEOUT"),
}

OS_PLACES_API_KEY = os.environ.get("OS_PLACES_API_KEY")

ZENDESK_API_USERNAME = os.environ.get("ZENDESK_API_USERNAME")
ZENDESK_API_TOKEN = os.environ.get("ZENDESK_API_TOKEN")
ZENDESK_DEFAULT_REQUESTER = 649762516  # anonymous feedback <noreply@ministryofjustice.zendesk.com>

GDS_GA_ID = os.environ.get("GDS_GA_ID")
MOJ_GTM_ID = os.environ.get("MOJ_GTM_ID")
MOJ_GTM_AUTH = os.environ.get("MOJ_GTM_AUTH")
MOJ_GTM_PREVIEW = os.environ.get("MOJ_GTM_PREVIEW")

CACHE_TYPE = "simple"

EXTENSIONS = []

CLA_ENV = os.environ.get("CLA_ENV", "dev")

LANGUAGES = [("en", "English"), ("cy", "Welsh")]


def config_path(x):
    return os.path.join(PROJECT_ROOT, "config", "forms", x, "forms_config.yml")


FORM_CONFIG_TRANSLATIONS = {code: config_path(code) for code, label in LANGUAGES}


TIMEZONE = "Europe/London"

LAALAA_API_HOST = os.environ.get("LAALAA_API_HOST", "https://prod.laalaa.dsd.io")
# Remove the SMTP bits after the code has been removed
MAIL_SERVER = os.environ.get("SMTP_HOST")
MAIL_PORT = os.environ.get("SMTP_PORT", 465)
MAIL_USE_TLS = False
MAIL_USE_SSL = True

MAIL_USERNAME = os.environ.get("SMTP_USER")
MAIL_PASSWORD = os.environ.get("SMTP_PASSWORD")

MAIL_DEFAULT_SENDER = ("Civil Legal Advice", "no-reply@civillegaladvice.service.gov.uk")
GOVUK_NOTIFY_API_KEY = os.environ.get("GOVUK_NOTIFY_API_KEY")

GOVUK_NOTIFY_TEMPLATES = {
    "PUBLIC_CALLBACK_NOT_REQUESTED": os.environ.get(
        "GOVUK_NOTIFY_TEMPLATE_PUBLIC_CALLBACK_NOT_REQUESTED", "382cc41c-b81d-4197-8819-2ad76522d03d"
    ),
    "PUBLIC_CALLBACK_WITH_NUMBER": os.environ.get(
        "GOVUK_NOTIFY_TEMPLATE_PUBLIC_CALLBACK_WITH_NUMBER", "b4cfa1b6-f1e9-44c1-9b02-f07ba896b669"
    ),
    "PUBLIC_CALLBACK_WITH_NO_NUMBER": os.environ.get(
        "GOVUK_NOTIFY_TEMPLATE_PUBLIC_CALLBACK_WITH_NO_NUMBER", "3e2926c5-1bdf-4eb3-b212-7f206f1d764d"
    ),
    "PUBLIC_CALLBACK_THIRD_PARTY": os.environ.get(
        "GOVUK_NOTIFY_TEMPLATE_PUBLIC_CALLBACK_THIRD_PARTY", "7ffc6de3-07bd-4232-b416-cf18d0abfec6"
    ),
    "PUBLIC_CONFIRMATION_NO_CALLBACK": os.environ.get(
        "GOVUK_NOTIFY_TEMPLATE_PUBLIC_CONFIRMATION_NO_CALLBACK", "1a56ee47-a200-43f9-bab2-e0852da0714b"
    ),
    "PUBLIC_CONFIRMATION_EMAIL_CALLBACK_REQUESTED": os.environ.get(
        "GOVUK_NOTIFY_TEMPLATE_PUBLIC_CONFIRMATION_EMAIL_CALLBACK_REQUESTED", "020ba10c-ac98-4b7c-a49f-1f129462506b"
    ),
    "PUBLIC_CONFIRMATION_EMAIL_CALLBACK_REQUESTED_THIRDPARTY": os.environ.get(
        "GOVUK_NOTIFY_TEMPLATE_PUBLIC_CONFIRMATION_EMAIL_CALLBACK_REQUESTED_THIRDPARTY",
        "ca425753-c31b-426b-a532-b864701b2178",
    ),
}

GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")
MAINTENANCE_MODE = os.environ.get("MAINTENANCE_MODE", "False").upper() == "TRUE"


def current_app_cache_factory(*args, **kwargs):
    from flask import current_app  # noqa: E402

    return current_app.cache


# Use Flasks current_app.cache to cache bank holidays lookups
CacheAdapter.set_adapter_factory(current_app_cache_factory)

# Use the Flask babel extension to translate strings in cla_common
TranslationAdapter.set_adapter_factory(lambda: _)

# local.py overrides all the common settings.
try:
    from cla_public.config.local import *  # noqa: F401,F403
except ImportError:
    pass
