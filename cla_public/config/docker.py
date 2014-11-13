from cla_public.config.base import *


DEBUG = os.environ.get('SET_DEBUG', False) == 'True'

SECRET_KEY = os.environ['SECRET_KEY']

HOST_NAME = os.environ['HOST_NAME']

BACKEND_API = {
    'url': os.environ['BACKEND_BASE_URI']
}
