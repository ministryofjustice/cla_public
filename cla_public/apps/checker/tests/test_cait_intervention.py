import os
import unittest
import mock
import requests
import json
import flask

app = flask.Flask(__name__)

from cla_public.apps.checker.cait_intervention import get_cait_params

# Load dummy config data
configs = {}
for state in ['on', 'off', 'invalid']:
    with open(os.path.join(os.path.dirname(__file__), 'data/cait_intervention/cait_intervention_config-' + state + '.json')) as json_data:
        configs[state] = json.load(json_data)


# Provide a mock response for the tests
def setup_mock(json, status):
    def mocked_requests_get(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json
                self.status_code = status

            def json(self):
                return self.json_data
        return MockResponse(json, status)
    return mocked_requests_get

# Call the cait intervention code with standard params
def call_cait_params():
    return get_cait_params({'foo': 'bar', 'truncate': 5}, 'Family', [], {})
# Params unaffected by cait intervention
default_params_out = {'foo': 'bar', 'truncate': 5}


class TestCaitIntervention(unittest.TestCase):

    # Simulate a config file not being returned
    @mock.patch('cla_public.apps.checker.cait_intervention.requests.get', side_effect=setup_mock(None, 404))
    def test_config_missing(self, mock_get):
        params = call_cait_params()
        self.assertEqual(params, default_params_out)

    # Simulate a config file being returned that is invalid
    @mock.patch('cla_public.apps.checker.cait_intervention.requests.get', side_effect=setup_mock(configs['invalid'], 200))
    def test_config_missing(self, mock_get):
        params = call_cait_params()
        self.assertEqual(params, default_params_out)

    # Simulate a config file being returned that has off values
    @mock.patch('cla_public.apps.checker.cait_intervention.requests.get', side_effect=setup_mock(configs['off'], 200))
    def test_config_missing(self, mock_get):
        params = call_cait_params()
        self.assertEqual(params, default_params_out)
    
    # Simulate a config file being returned that has on values
    @mock.patch('cla_public.apps.checker.cait_intervention.requests.get', side_effect=setup_mock(configs['on'], 200))
    def test_config_on(self, mock_get):
  
        # Shouldn't run if user has gone through financial check
        with app.test_request_context('/scope/checker/family'):
            params = call_cait_params()
            self.assertEqual(params, default_params_out)

        # Finally, check updated params
        with app.test_request_context('/scope/refer/family'):
            params = call_cait_params()
            self.assertEqual(params.get('foo'), 'bar')
            self.assertEqual(params.get('truncate'), 5)
            self.assertEqual(params.get('info_tools'), True)
            self.assertEqual(params.get('cait_variant'), 'default')
            survey = params.get('cait_survey')
            self.assertEqual(survey.get('heading'), 'heading')
            self.assertEqual(survey.get('body'), 'body <a href="http://survey/default" target="cait_survey">answer some questions</a>?')
            # call again and get the other variant
            params = call_cait_params()
            self.assertEqual(params.get('cait_variant'), 'variant-plain')
            self.assertEqual(params.get('truncate'), 6)
            # call again and get the default once more
            params = call_cait_params()
            self.assertEqual(params.get('cait_variant'), 'default')
            self.assertEqual(params.get('truncate'), 5)
