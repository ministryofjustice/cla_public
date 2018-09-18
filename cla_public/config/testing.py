from cla_public.config.common import *


DEBUG = False

SESSION_COOKIE_SECURE = False

TESTING = True

LOGGING['loggers']['']['level'] = 'WARNING'

WTF_CSRF_ENABLED = False

LAALAA_API_HOST = os.environ.get('LAALAA_API_HOST', 'http://localhost:8001')
