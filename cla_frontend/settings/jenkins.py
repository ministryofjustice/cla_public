from .testing import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Marco Fucci', 'marco.fucci@digital.justice.co.uk'),
    ('Rai Kotecha', 'ravi.kotecha@digital.justice.gov.uk'),
)

MANAGERS = ADMINS

INSTALLED_APPS += ('django_jenkins',)

JENKINS_TASKS = (
    'django_jenkins.tasks.with_coverage',
)

DATABASES = {}

#JENKINS_TEST_RUNNER = 'core.test_runners.AdvancedCITestSuiteRunner'

#HOST_NAME = ""
