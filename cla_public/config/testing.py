from cla_public.config.common import *


DEBUG = False

SESSION_COOKIE_SECURE = False

TESTING = True

LOGGING['loggers'] = {
    '': {
        'handlers': ['console'],
        'level': 'INFO'
    }
}

WTF_CSRF_ENABLED = False
