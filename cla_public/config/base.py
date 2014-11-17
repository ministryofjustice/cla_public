import os


DEBUG = False

TESTING = False

LOG_LEVEL = 'WARNING'

SECRET_KEY = "e\x1bU3\xbc\x00\xb0\xae\x07z~D\x03\xcc'\x04\x1f\xcd\xe8\xee\x83\xe6\x9b\x19"

SESSION_COOKIE_SECURE = True

APP_SETTINGS = {
    'app_title': 'Civil Legal Aid',
    'proposition_title': 'Civil Legal Aid'
}

BACKEND_API = {
    'url': 'http://localhost:8000/checker/api/v1/'
}

RAVEN_CONFIG = {
    'dsn': os.environ.get('RAVEN_CONFIG_DSN'),
    'site': os.environ.get('RAVEN_CONFIG_SITE')
}

EXTENSIONS = []

# local.py overrides all the common settings.
try:
    from cla_public.config.local import *
except ImportError:
    pass
