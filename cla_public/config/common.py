import os
import datetime


DEBUG = False

TESTING = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'logstash': {
            '()': 'logstash_formatter.LogstashFormatter'
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'cla_public.libs.logging_filters.RequireDebug',
            'debug': False
        },
        'require_debug_true': {
            '()': 'cla_public.libs.logging_filters.RequireDebug',
            'debug': True
        }
    },
    'handlers': {
        'production_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/tmp/app.log',
            'maxBytes': 1024 * 1024 * 5,  # 5MB
            'backupCount': 7,
            'formatter': 'logstash',
            'filters': ['require_debug_false'],
        },
        'debug_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/tmp/debug.log',
            'maxBytes': 1024 * 1024 * 5,  # 5MB
            'backupCount': 7,
            'formatter': 'verbose',
            'filters': ['require_debug_true'],
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'stream': 'ext://sys.stdout'
        }
    },
    'loggers': {
        '': {
            'handlers': ['production_file', 'debug_file'],
            'level': 'DEBUG'
        }
    }
}

SECRET_KEY = os.urandom(24)

# Should be True when served over HTTPS, False otherwise (or CSRF will break)
SESSION_COOKIE_SECURE = True

PERMANENT_SESSION_LIFETIME = datetime.timedelta(minutes=5)

APP_SETTINGS = {
    'app_title': 'Civil Legal Aid',
    'proposition_title': 'Civil Legal Aid'
}

# Timeout for api get requests so they don't hang waiting for a response
API_CLIENT_TIMEOUT = 10

BACKEND_API = {
    'url': 'http://localhost:8000/checker/api/v1/'
}

SENTRY_DSN = os.environ.get('RAVEN_CONFIG_DSN', '')
SENTRY_SITE_NAME = os.environ.get('RAVEN_CONFIG_SITE', '')

ADDRESSFINDER_API_HOST = os.environ.get('ADDRESSFINDER_API_HOST')
ADDRESSFINDER_API_TOKEN = os.environ.get('ADDRESSFINDER_API_TOKEN')

GA_ID = os.environ.get('GA_ID')

CACHE_CONFIG = {
    'CACHE_TYPE': 'simple'
}

EXTENSIONS = []

# local.py overrides all the common settings.
try:
    from cla_public.config.local import *
except ImportError:
    pass
