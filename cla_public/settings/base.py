import sys
import os
from os.path import join, abspath, dirname

# PATH vars

here = lambda *x: join(abspath(dirname(__file__)), *x)
PROJECT_ROOT = here("..")
root = lambda *x: join(abspath(PROJECT_ROOT), *x)

APPS_ROOT = root('apps')

sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, APPS_ROOT)


# ENVIRON values

from django.core.exceptions import ImproperlyConfigured

# .env_values.py contains secrets and host config values usually stored
# in a different place
try:
    import env_values
except ImportError:
    env_values = None


def get_env_value(var_name):
    """ Get the env value `var_name` or return exception """
    try:
        return getattr(env_values, var_name)
    except AttributeError:
        raise ImproperlyConfigured("Environment value %s not found" % var_name)


DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = ()

MANAGERS = ADMINS

DATABASES = {}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = root('assets', 'uploads')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = root('static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    root('assets'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '(W)*6GwxNiYn<B*ug<U9jdYNDY(#vu(:Y&NthqqPk?^CM=ee?z'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'core.middleware.AnonymousUserSessionSecurityMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS =  (
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    'django.core.context_processors.request',
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "cla_public.apps.core.context_processors.globals"
 )

ROOT_URLCONF = 'cla_public.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'cla_public.wsgi.application'

# TODO change this ?
SESSION_ENGINE = 'django.contrib.sessions.backends.file'

TEMPLATE_DIRS = (
    root('templates'),
)

INSTALLED_APPS = (
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'widget_tweaks',
    'form_utils',
    'session_security'
)

PROJECT_APPS = (
    'moj_template',
    'core',
    'checker',
    'cla_common'
)

INSTALLED_APPS += PROJECT_APPS

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    'handlers': {
        'production_file':{
            'level' : 'INFO',
            'class' : 'logging.handlers.RotatingFileHandler',
            'filename' : '/var/log/wsgi/app.log',
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount' : 7,
            'formatter': 'verbose',
            'filters': ['require_debug_false'],
        },
        'debug_file':{
            'level' : 'DEBUG',
            'class' : 'logging.handlers.RotatingFileHandler',
            'filename' : '/var/log/wsgi/debug.log',
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount' : 7,
            'formatter': 'verbose',
            'filters': ['require_debug_true'],
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        '': {
            'handlers': ['production_file','debug_file'],
            'level': 'DEBUG',
        },
    }
}


BACKEND_BASE_URI = 'http://127.0.0.1:8000'

GA_ID = ''


# Settings for django-session-security.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SECURITY_WARN_AFTER = 3360
SESSION_SECURITY_EXPIRE_AFTER = 3600

RAVEN_CONFIG = {
    'dsn': os.environ.get('RAVEN_CONFIG_DSN', ''),
    'site': os.environ.get('RAVEN_CONFIG_SITE', '')
}

if 'RAVEN_CONFIG_DSN' in os.environ:
    MIDDLEWARE_CLASSES = (
        'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',
        'raven.contrib.django.raven_compat.middleware.Sentry404CatchMiddleware',
    ) + MIDDLEWARE_CLASSES

# EMAILS

# importing test settings file if necessary (TODO chould be done better)
if len(sys.argv) > 1 and 'test' in sys.argv[1]:
    from .testing import *

# .local.py overrides all the common settings.
try:
    from .local import *
except ImportError:
    pass


