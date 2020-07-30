import os

from cla_public.config.common import *  # noqa F100

settings_required = (
    "ZENDESK_API_USERNAME",
    "ZENDESK_API_TOKEN",
    "SMTP_HOST",
    "SMTP_USER",
    "SMTP_PASSWORD",
    "RAVEN_CONFIG_DSN",
    "RAVEN_CONFIG_SITE",
    "BACKEND_BASE_URI",
    "LAALAA_API_HOST",
    "GOOGLE_MAPS_API_KEY",
)

for key in settings_required:
    if key not in os.environ:
        raise Exception("'{}' Environment variable is required. please provide".format(key))

DEBUG = os.environ.get("SET_DEBUG", False) == "True"

SESSION_COOKIE_SECURE = os.environ.get("CLA_ENV", "") in ["production", "staging"]

HOST_NAME = os.environ.get("HOST_NAME") or os.environ.get("HOSTNAME")

LOGGING["handlers"]["console"]["formatter"] = "logstash"  # noqa
LOGGING["loggers"] = {"": {"handlers": ["console"], "level": os.environ.get("LOG_LEVEL", "INFO")}}  # noqa
