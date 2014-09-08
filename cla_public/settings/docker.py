from .base import *
import os
import iptools

SECRET_KEY = os.environ["SECRET_KEY"]

DEBUG = bool(os.environ.get('SET_DEBUG', False))

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Marco Fucci', 'marco.fucci@digital.justice.co.uk'),
    ('Rai Kotecha', 'ravi.kotecha@digital.justice.gov.uk'),
)

MANAGERS = ADMINS


HOST_NAME = os.environ["HOST_NAME"]

BACKEND_BASE_URI = os.environ["BACKEND_BASE_URI"]

ALLOWED_HOSTS = [
    HOST_NAME
]

# Allow MOJ_DSD IPS to see TEMPLATE_DEBUG
INTERNAL_IPS = iptools.IpRangeList(
    '12.137.32.0/20',
    '81.134.202.16/28',
    '85.118.8.128/26',
    '213.205.229.219/32',
    '127.0.0.1'
)

GA_ID = os.environ["GA_ID"]

