from cla_public.config.common import *


DEBUG = False

SESSION_COOKIE_SECURE = False

TESTING = True

LOGGING['loggers']['']['level'] = 'WARNING'

WTF_CSRF_ENABLED = False

BACKEND_API = {
    'url': 'http://localhost:{port}/checker/api/v1/'.format(
        port=os.environ.get('CLA_BACKEND_PORT', 8000))
}
