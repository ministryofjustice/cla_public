from copy import copy
import json
import os
import unittest

import mock
from requests.exceptions import ConnectionError, Timeout

from cla_public.app import create_app
from cla_public.apps.checker.cait_intervention import get_cait_params

# Load dummy config data
configs = {}
for state in ['on', 'off']:
    with open(
        os.path.join(
            os.path.dirname(__file__),
            'data/cait_intervention/cait_intervention_config-%s.json' % state)
    ) as json_data:
        configs[state] = json_data.read()


# Provide a mock response for the tests
def setup_mock(mock_json, mock_status):
    def mocked_requests_get(*args, **kwargs):
        class MockResponse:
            def __init__(self, mock_json, mock_status):
                self.json_data = mock_json
                self.status_code = mock_status

            def json(self):
                return json.loads(self.json_data)
        return MockResponse(mock_json, mock_status)
    return mocked_requests_get


# Call the cait intervention code with standard params
def call_cait_params():
    return get_cait_params('Family', [], ['n10', 'n5', 'n5'])


# Params unaffected by cait intervention
DEFAULT_PARAMS_OUT = {'foo': 'bar', 'truncate': 5}
PARAMS_OUT_WITH_SURVEY = {'foo': 'bar', 'truncate': 5, 'cait_survey':{}}
# Path to requests.get
REQUESTS_GET = 'cla_public.apps.checker.cait_intervention.requests.get'


class TestCaitIntervention(unittest.TestCase):

    def setUp(self):
        self.app = create_app('config/testing.py')
        self.app.test_request_context().push()

    # Simulate a config file not being returned
    @mock.patch(REQUESTS_GET, setup_mock('', 404))
    def test_config_missing(self):
        with self.app.test_request_context('/scope/refer/family'):
            params = copy(DEFAULT_PARAMS_OUT)
            params.update(call_cait_params())
            self.assertEqual(params, DEFAULT_PARAMS_OUT)

    # Simulate a config file being returned that is invalid
    @mock.patch(REQUESTS_GET, setup_mock('', 200))
    def test_config_invalid(self):
        with self.app.test_request_context('/scope/refer/family'):
            params = copy(DEFAULT_PARAMS_OUT)
            params.update(call_cait_params())
            self.assertEqual(params, DEFAULT_PARAMS_OUT)

    # Simulate a config file being returned that has off values
    @mock.patch(REQUESTS_GET, setup_mock(configs['off'], 200))
    def test_config_off(self):
        with self.app.test_request_context('/scope/refer/family'):
            params = copy(DEFAULT_PARAMS_OUT)
            params.update(call_cait_params())
            self.assertEqual(params, PARAMS_OUT_WITH_SURVEY)

    # Simulate a config file being returned that has on values
    @mock.patch(REQUESTS_GET, setup_mock(configs['on'], 200))
    def test_config_on(self):

        # Finally, check updated params
        with self.app.test_request_context('/scope/refer/family'):
            params = copy(DEFAULT_PARAMS_OUT)
            params.update(call_cait_params())
            self.assertEqual(params.get('foo'), 'bar')
            self.assertEqual(params.get('truncate'), 5)
            self.assertEqual(params.get('info_tools'), True)
            self.assertEqual(params.get('cait_variant'), 'default')
            survey = params.get('cait_survey')
            self.assertEqual(survey.get('heading'), 'heading')
            self.assertEqual(
                survey.get('body'),
                'body <a href="http://survey/default" target="cait_survey">'
                'answer some questions</a>?')

            # call again and get the other variant
            params = copy(DEFAULT_PARAMS_OUT)
            params.update(call_cait_params())
            self.assertEqual(params.get('cait_variant'), 'variant-plain')
            self.assertEqual(params.get('truncate'), 6)

            # call again and get the default once more
            params = copy(DEFAULT_PARAMS_OUT)
            params.update(call_cait_params())
            self.assertEqual(params.get('cait_variant'), 'default')
            self.assertEqual(params.get('truncate'), 5)

        # Shouldn't run if user has gone through financial check
        with self.app.test_request_context('/scope/checker/family'):
            params = copy(DEFAULT_PARAMS_OUT)
            params.update(call_cait_params())
            self.assertEqual(params, DEFAULT_PARAMS_OUT)

    @mock.patch(REQUESTS_GET, setup_mock('{"fdfd', 200))
    def test_invalid_json(self):
        params = call_cait_params()
        self.assertEqual(params, {})
