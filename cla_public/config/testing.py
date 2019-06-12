import os

from cla_public.config.common import *  # noqa F403


DEBUG = False

SESSION_COOKIE_SECURE = False

TESTING = True

LOGGING["loggers"][""]["level"] = "WARNING"  # noqa F405

WTF_CSRF_ENABLED = False

LAALAA_API_HOST = os.environ.get("LAALAA_API_HOST", "http://localhost:8001")
