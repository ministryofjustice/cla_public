from .base import *
import iptools

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Marco Fucci', 'marco.fucci@digital.justice.co.uk'),
    ('Ravi Kotecha', 'ravi.kotecha@digital.justice.gov.uk'),
)

MANAGERS = ADMINS


HOST_NAME = "http://cla-public.dsd.io"

BACKEND_BASE_URI = 'http://cla-backend.dsd.io'

ALLOWED_HOSTS = [
    HOST_NAME
]

# Allow MOJ_DSD IPS to see TEMPLATE_DEBUG
INTERNAL_IPS = iptools.IpRangeList(
    '12.137.32.0/20',
    '81.134.202.16/28',
    '85.118.8.128/26',
    '127.0.0.1'
)

GA_ID = 'UA-37377084-13'

RAVEN_CONFIG = {
    'dsn': 'https://675e5dd8e19748ec8a36febb6982fa96:c4db076533774732b754cd77b0464d58@app.getsentry.com/26720',
}

INSTALLED_APPS = INSTALLED_APPS + (
    'raven.contrib.django.raven_compat',
)
