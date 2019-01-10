from copy import copy
import json
import os
import unittest

import mock

from cla_public.app import create_app
from cla_public.apps.checker.cait_intervention import get_cait_params

# Load dummy config data
configs = {}
for state in ["on", "off"]:
    with open(
        os.path.join(os.path.dirname(__file__), "data/cait_intervention/cait_intervention_config-%s.json" % state)
    ) as json_data:
        configs[state] = json_data.read()


# Provide a mock response for the tests
def setup_mock_response(mock_json, mock_status):
    def mocked_requests_get(*args, **kwargs):
        class MockResponse:
            def __init__(self, mock_json, mock_status):
                self.json_data = mock_json
                self.status_code = mock_status

            def json(self):
                return json.loads(self.json_data)

        return MockResponse(mock_json, mock_status)

    return mocked_requests_get


def setup_organisation_list(organisation_list=[]):
    def mocked_organisation_list(*args, **kwargs):
        return organisation_list

    return mocked_organisation_list


# Call the cait intervention code with standard params
def call_cait_params(choices=[]):
    return get_cait_params("Family", [], choices)
    # return get_cait_params('Family', [], ['n10', 'n5', 'n5'])


# Path to requests.get
REQUESTS_GET = "cla_public.apps.checker.cait_intervention.requests.get"
ORGANISATION_LIST = "cla_public.apps.checker.views.get_organisation_list"

# Scope paths
SCOPE_REFER = "/scope/refer/family"
SCOPE_CHECKER = "/scope/checker/family"

# Params unaffected by cait intervention
DEFAULT_PARAMS_OUT = {"truncate": 5}

DEFAULT_SURVEY = "http://survey/default"


class TestCaitIntervention(unittest.TestCase):
    def setUp(self):
        self.app = create_app("config/testing.py")
        self.client = self.app.test_client()
        self.app.test_request_context().push()

    @mock.patch(ORGANISATION_LIST, setup_organisation_list())
    def test_direct_pathway(self):
        response = self.client.get("/scope/refer/family")
        self.assertEqual(response.status_code, 200)

    # Simulate a config file not being returned
    @mock.patch(REQUESTS_GET, setup_mock_response("", 404))
    def test_config_missing(self):
        with self.app.test_request_context(SCOPE_REFER):
            params = copy(DEFAULT_PARAMS_OUT)
            params.update(call_cait_params())
            self.assertEqual(params, DEFAULT_PARAMS_OUT)

    # Simulate a config file being returned that is invalid
    @mock.patch(REQUESTS_GET, setup_mock_response('{"fdfd', 200))
    def test_invalid_json(self):
        with self.app.test_request_context(SCOPE_REFER):
            params = copy(DEFAULT_PARAMS_OUT)
            params.update(call_cait_params())
            self.assertEqual(params, DEFAULT_PARAMS_OUT)

    # Simulate a config file being returned that has off values
    @mock.patch(ORGANISATION_LIST, setup_organisation_list())
    @mock.patch(REQUESTS_GET, setup_mock_response(configs["off"], 200))
    def test_config_off(self):
        with self.app.test_request_context(SCOPE_REFER):
            params = copy(DEFAULT_PARAMS_OUT)
            params.update(call_cait_params())
            self.assertEqual(params, DEFAULT_PARAMS_OUT)

            # check the exit page actually renders
            response = self.client.get("/scope/refer/family")
            self.assertEqual(response.status_code, 200)

    # Simulate a config file being returned that has on values
    @mock.patch(ORGANISATION_LIST, setup_organisation_list())
    @mock.patch(REQUESTS_GET, setup_mock_response(configs["on"], 200))
    def test_config_on(self):

        # Finally, check updated params
        with self.app.test_request_context(SCOPE_REFER):
            params = copy(DEFAULT_PARAMS_OUT)
            params.update(call_cait_params())
            self.assertEqual(params.get("truncate"), 5)
            self.assertEqual(params.get("info_tools"), True)
            self.assertEqual(params.get("cait_variant"), "default")
            survey = params.get("cait_survey")
            self.assertEqual(survey.get("heading"), "heading")
            self.assertEqual(
                survey.get("body"),
                'body <a href="http://survey/default" target="cait_survey">' "answer some questions</a>?",
            )
            self.assertEqual(params.get("cait_css"), "body { background: red; }")
            self.assertEqual(params.get("cait_js"), "alert('foo')")
            journey = params.get("cait_journey", {})
            self.assertEqual(journey.get("uuid"), None)
            self.assertEqual(journey.get("nodes"), None)
            self.assertEqual(journey.get("last_node"), None)

            # call again and get the other variant
            params = copy(DEFAULT_PARAMS_OUT)
            params.update(call_cait_params())
            self.assertEqual(params.get("cait_variant"), "variant-plain")
            self.assertEqual(params.get("truncate"), 6)
            journey = params.get("cait_journey", {})
            # should be a uuid, but no node info
            self.assertNotEqual(journey.get("uuid"), None)
            self.assertEqual(journey.get("nodes"), None)
            self.assertEqual(journey.get("last_node"), None)

            # call again and get the default once more
            params = copy(DEFAULT_PARAMS_OUT)
            params.update(call_cait_params())
            self.assertEqual(params.get("cait_variant"), "default")
            self.assertEqual(params.get("truncate"), 5)

            # level 1 node we want to match
            params = copy(DEFAULT_PARAMS_OUT)
            params.update(call_cait_params(["n4334", "n105", "n572"]))
            survey = params.get("cait_survey")
            self.assertIn("http://survey/a", survey.get("body"))
            journey = params.get("cait_journey", {})
            # should be a uuid and node info
            self.assertNotEqual(journey.get("uuid"), None)
            self.assertEqual(journey.get("nodes"), "n4334/n105/n572")
            self.assertEqual(journey.get("last_node"), "n572")

            # level 1 node we don't want to match
            params = copy(DEFAULT_PARAMS_OUT)
            params.update(call_cait_params(["n4334", "n105a", "n572"]))
            survey = params.get("cait_survey")
            self.assertIn(DEFAULT_SURVEY, survey.get("body"))

            # level 2 node we want to match
            params = copy(DEFAULT_PARAMS_OUT)
            params.update(call_cait_params(["n4334", "n97", "n49"]))
            survey = params.get("cait_survey")
            self.assertIn("http://survey/d", survey.get("body"))

            # level 2 node we don't want to match
            params = copy(DEFAULT_PARAMS_OUT)
            params.update(call_cait_params(["n4334", "n97", "n49a"]))
            survey = params.get("cait_survey")
            self.assertIn(DEFAULT_SURVEY, survey.get("body"))

            # check the exit page actually renders
            response = self.client.get("/scope/refer/family")
            self.assertEqual(response.status_code, 200)

        # Shouldn't run if user has gone through financial check
        with self.app.test_request_context(SCOPE_CHECKER):
            params = copy(DEFAULT_PARAMS_OUT)
            params.update(call_cait_params())
            self.assertEqual(params, DEFAULT_PARAMS_OUT)
