from cla_public.config.base import *


DEBUG = os.environ.get('SET_DEBUG', False) == 'True'

SECRET_KEY = os.environ['SECRET_KEY']

# TODO - change this to True when serving over HTTPS
SESSION_COOKIE_SECURE = False

HOST_NAME = os.environ['HOST_NAME']

BACKEND_API = {
    'url': os.environ['BACKEND_BASE_URI'] + '/checker/api/v1/'
}
