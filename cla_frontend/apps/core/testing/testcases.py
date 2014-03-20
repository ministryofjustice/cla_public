import mock

from django.test.testcases import SimpleTestCase


class CLATestCase(SimpleTestCase):
    @mock.patch('checker.forms.base.connection')
    def __call__(self, result, mocked_connection, *args, **kwargs):
        self.mocked_connection = mocked_connection

        super(CLATestCase, self).__call__(result, *args, **kwargs)
