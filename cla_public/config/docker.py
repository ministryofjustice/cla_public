from cla_public.config.common import *


DEBUG = os.environ.get('SET_DEBUG', False) == 'True'

SECRET_KEY = os.environ['SECRET_KEY']

# TODO - change this to True when serving over HTTPS
SESSION_COOKIE_SECURE = False

HOST_NAME = os.environ['HOST_NAME']

BACKEND_API = {
    'url': os.environ['BACKEND_BASE_URI'] + '/checker/api/v1/'
}

LOGGING['handlers']['production_file']['filename'] = '/var/log/wsgi/app.log'
LOGGING['handlers']['debug_file']['filename'] = '/var/log/wsgi/debug.log'
