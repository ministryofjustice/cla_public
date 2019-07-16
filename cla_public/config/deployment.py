import os

settings_required = (
    "ZENDESK_API_USERNAME",
    "ZENDESK_API_TOKEN",
    "RAVEN_CONFIG_DSN",
    "RAVEN_CONFIG_SITE",
    "BACKEND_BASE_URI",
    "LAALAA_API_HOST",
    "GOV_NOTIFY_API_KEY",
    "GOV_NOTIFY_TEMPLATE_CONFIRMATION",
)

for key in settings_required:
    if not os.environ.get(key):
        raise Exception("'{}' Environment variable is required. please provide".format(key))

from cla_public.config.common import *


DEBUG = os.environ.get("SET_DEBUG", False) == "True"

SESSION_COOKIE_SECURE = os.environ.get("CLA_ENV", "") in ["prod", "staging"]

HOST_NAME = os.environ.get("HOST_NAME") or os.environ.get("HOSTNAME")

LOGGING["handlers"]["console"]["formatter"] = "logstash"
LOGGING["loggers"] = {"": {"handlers": ["console"], "level": os.environ.get("LOG_LEVEL", "INFO")}}
