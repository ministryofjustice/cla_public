import os

os.environ.setdefault("SMTP_HOST", "")
os.environ.setdefault("SMTP_USER", "")
os.environ.setdefault("SMTP_PASSWORD", "")
os.environ.setdefault("RAVEN_CONFIG_DSN", "")
os.environ.setdefault("RAVEN_CONFIG_SITE", "")
os.environ.setdefault("ZENDESK_API_USERNAME", "")
os.environ.setdefault("ZENDESK_API_TOKEN", "")

from cla_public.config.common import *


DEBUG = False

SESSION_COOKIE_SECURE = False

TESTING = True

LOGGING["loggers"][""]["level"] = "WARNING"

WTF_CSRF_ENABLED = False

LAALAA_API_HOST = os.environ.get("LAALAA_API_HOST", "http://localhost:8001")
