import unittest
from mock import patch

from requests.exceptions import ConnectionError, Timeout

from cla_public.app import create_app


class TestApiTimeout(unittest.TestCase):

    def setUp(self):
        app = create_app('config/testing.py')
        app.test_request_context().push()
        self.client = app.test_client()
        with self.client.session_transaction() as session:
            session['test'] = True

    def test_form_error_on_api_timeout(self):
        def timeout(*args, **kwargs):
            raise Timeout()
        with patch('requests.Session.send', timeout) as t:
            try:
                response = self.client.post('/problem', data={
                    'categories': ['debt']})
            except Timeout:
                self.fail('Timeout not caught')
            except ConnectionError:
                self.fail('ConnectionError not caught')

            self.assertIn('There was an error submitting your data. Please check '
                          'and try again.', response.data)
