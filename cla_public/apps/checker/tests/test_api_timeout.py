import unittest
from mock import patch

from requests.exceptions import ConnectionError, Timeout

from cla_public.app import create_app
from cla_public.apps.checker.constants import NO, YES


class TestApiTimeout(unittest.TestCase):

    def setUp(self):
        app = create_app('config/testing.py')
        app.test_request_context().push()
        self.client = app.test_client()
        with self.client.session_transaction() as session:
            session['test'] = True
            session.checker['test'] = True

    def test_form_error_on_api_timeout(self):
        def timeout(*args, **kwargs):
            raise Timeout()
        with patch('requests.Session.send', timeout) as t:
            try:
                response = self.client.post('/about', data={
                    'have_valuables': NO,
                    'have_children': NO,
                    'csrf_token': NO,
                    'is_employed': NO,
                    'have_partner': YES,
                    'have_dependants': NO,
                    'in_dispute': NO,
                    'have_savings': NO,
                    'partner_is_self_employed': YES,
                    'partner_is_employed': NO,
                    'aged_60_or_over': NO,
                    'is_self_employed': NO,
                    'on_benefits': NO,
                    'own_property': NO,
                })
            except Timeout:
                self.fail('Timeout not caught')
            except ConnectionError:
                self.fail('ConnectionError not caught')

            self.assertIn('There was an error submitting your data. Please check '
                          'and try again.', response.data)
