from django.test.runner import DiscoverRunner

from django.conf import settings


class NoDbTestRunner(DiscoverRunner):
    """ A test runner to test without database creation """
    def __init__(self, *args, **kwargs):
        kwargs['top_level'] = settings.APPS_ROOT
        super(NoDbTestRunner, self).__init__(*args, **kwargs)

    def build_suite(self, test_labels=None, extra_tests=None, **kwargs):
        test_labels = test_labels or ['apps']
        return super(NoDbTestRunner, self).build_suite(test_labels=test_labels, extra_tests=extra_tests, **kwargs)

    def setup_databases(self, **kwargs):
        """ Override the database creation defined in parent class """
        pass

    def teardown_databases(self, old_config, **kwargs):
        """ Override the database teardown defined in parent class """
        pass
