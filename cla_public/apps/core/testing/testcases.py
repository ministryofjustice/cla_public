import mock

from django.test.testcases import SimpleTestCase


class CLATestCase(SimpleTestCase):
    @mock.patch('checker.views.connection')
    @mock.patch('checker.forms.base.connection')
    def __call__(self, result, mocked_connection, mocked_wizard_connection, *args, **kwargs):
        self.mocked_connection = mocked_connection
        self.mocked_wizard_connection = mocked_wizard_connection

        super(CLATestCase, self).__call__(result, *args, **kwargs)
