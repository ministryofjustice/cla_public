from cla_public.config.common import *


DEBUG = os.environ.get('SET_DEBUG', False) == 'True'

SECRET_KEY = os.environ['SECRET_KEY']

# TODO - change this to True when serving over HTTPS
SESSION_COOKIE_SECURE = os.environ.get('CLA_ENV', '') in ['prod', 'staging']

HOST_NAME = os.environ.get('HOST_NAME') or os.environ.get('HOSTNAME')

BACKEND_API = {
    'url': os.environ['BACKEND_BASE_URI'] + '/checker/api/v1/'
}

if DEBUG:
    LOGGING['handlers']['debug_file'] = {
        'level': 'DEBUG',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': '/var/log/wsgi/debug.log',
        'maxBytes': 1024 * 1024 * 5,  # 5MB
        'backupCount': 7,
        'formatter': 'verbose'}
    LOGGING['loggers'] = {
        '': {
            'handlers': ['debug_file'],
            'level': 'DEBUG'
        }
    }

else:
    LOGGING['handlers']['production_file'] = {
        'level': 'INFO',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': '/var/log/wsgi/app.log',
        'maxBytes': 1024 * 1024 * 5,  # 5MB
        'backupCount': 7,
        'formatter': 'logstash'}
    LOGGING['loggers'] = {
        '': {
            'handlers': ['production_file'],
            'level': 'DEBUG'
        }
    }
