from cla_public.config.base import *


DEBUG = True

SESSION_COOKIE_SECURE = False

TESTING = True

LOGGING['loggers'] = {
    '': {
        'handlers': ['console'],
        'level': 'WARNING'
    }
}

WTF_CSRF_ENABLED = False
