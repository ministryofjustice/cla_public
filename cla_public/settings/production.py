from .base import *


DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('MoJ', 'Your email'),
)

MANAGERS = ADMINS


DATABASES = { }

RAVEN_CONFIG = {
    'dsn': 'https://4474bfcf88af4af6b77cd2f72d7d0536:9f232f754a92412a9010b6cc7e106559@app.getsentry.com/26721',
}

INSTALLED_APPS = INSTALLED_APPS + (
    'raven.contrib.django.raven_compat',
)
