import unittest
from mock import Mock

from requests.exceptions import ConnectionError, Timeout

from cla_public.app import create_app
from cla_public.apps.checker import api


class TestApiTimeout(unittest.TestCase):

    def setUp(self):
        app = create_app('config/testing.py')
        app.test_request_context().push()
        self.client = app.test_client()
        with self.client.session_transaction() as session:
            session['test'] = True
        self.monkeypatch_api_timeout()

    def monkeypatch_api_timeout(self):

        def timeout(*args):
            raise Timeout()

        mock_api = Mock()
        mock_api.eligibility_check.post = timeout
        self.original_api_conn = api.get_api_connection
        api.get_api_connection = lambda: mock_api

    def tearDown(self):
        self.remove_monkeypatches()

    def remove_monkeypatches(self):
        api.get_api_connection = self.original_api_conn

    def test_form_error_on_api_timeout(self):
        try:
            response = self.client.post('/problem', data={
                'categories': ['debt']})
        except Timeout:
            self.fail('Timeout not caught')
        except ConnectionError:
            self.fail('ConnectionError not caught')

        assert 'Server did not respond, please try again' in response.data
