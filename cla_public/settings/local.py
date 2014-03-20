from .base import *

SECRET_KEY = 'du)p2vbsvo58rjp#a=03u())&(460l93g48n=%mgaa%z7uin*-'

DEV_APPS = (
    'django_extensions',
    'debug_toolbar',
    'django_pdb',
)

INSTALLED_APPS += DEV_APPS
