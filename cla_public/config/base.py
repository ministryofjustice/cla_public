import os
import datetime


DEBUG = False

TESTING = False

LOG_LEVEL = 'WARNING'

SECRET_KEY = "e\x1bU3\xbc\x00\xb0\xae\x07z~D\x03\xcc'\x04\x1f\xcd\xe8\xee\x83\xe6\x9b\x19"

# Should be True when served over HTTPS, False otherwise (or CSRF will break)
SESSION_COOKIE_SECURE = True

PERMANENT_SESSION_LIFETIME = datetime.timedelta(minutes=5)

APP_SETTINGS = {
    'app_title': 'Civil Legal Aid',
    'proposition_title': 'Civil Legal Aid'
}

BACKEND_API = {
    'url': 'http://localhost:8000/checker/api/v1/'
}

SENTRY_DSN = os.environ.get('RAVEN_CONFIG_DSN', '')
SENTRY_SITE_NAME = os.environ.get('RAVEN_CONFIG_SITE', '')

ADDRESSFINDER_API_HOST = os.environ.get('ADDRESSFINDER_API_HOST',
    'http://addressfinder.dsd.io/')
ADDRESSFINDER_API_TOKEN = os.environ.get('ADDRESSFINDER_API_TOKEN',
    '7050a403a2fc1dcf74670acb3504d0f5cec50c5c')

CACHE_CONFIG = {
    'CACHE_TYPE': 'simple'
}

EXTENSIONS = []

# local.py overrides all the common settings.
try:
    from cla_public.config.local import *
except ImportError:
    pass
