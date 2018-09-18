from cla_public.config.common import *


DEBUG = os.environ.get('SET_DEBUG', False) == 'True'

SECRET_KEY = os.environ['SECRET_KEY']

SESSION_COOKIE_SECURE = os.environ.get('CLA_ENV', '') in ['prod', 'staging']

HOST_NAME = os.environ.get('HOST_NAME') or os.environ.get('HOSTNAME')

BACKEND_BASE_URI = os.environ['BACKEND_BASE_URI']

LAALAA_API_HOST = os.environ.get(
    'LAALAA_API_HOST', 'https://prod.laalaa.dsd.io')

LOGGING['handlers']['console']['formatter'] = 'logstash'
LOGGING['loggers'] = {
    '': {
        'handlers': ['console'],
        'level': os.environ.get('LOG_LEVEL', 'INFO')
    }
}
