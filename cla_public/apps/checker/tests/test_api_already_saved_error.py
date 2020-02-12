# coding: utf-8
import json
import unittest
from cla_public.apps.contact.views import session
from mock import patch
from slumber.exceptions import SlumberHttpBaseException

from cla_common.constants import ELIGIBILITY_STATES
from cla_public import app
from cla_public.apps.checker.api import post_to_case_api, AlreadySavedApiError
from cla_public.apps.contact.forms import ContactForm
from cla_public.apps.contact.views import Contact


def _mock_session_send(*args, **kwargs):
    raise SlumberHttpBaseException(
        content=json.dumps({"eligibility_check": ["Case with this Eligibility check already exists."]})
    )


def _mock_post_to_case_api(*args, **kwargs):
    raise AlreadySavedApiError()


def _mock_post_to_eligibility_check_api(*args, **kwargs):
    session.checker["eligibility_check"] = "EC"
    session.checker._eligibility = ELIGIBILITY_STATES.UNKNOWN


def _mock_get_case_ref_from_api(*args, **kwargs):
    session.checker["case_ref"] = "CR"


def _mock_post_to_is_eligible_api(*args, **kwargs):
    return ELIGIBILITY_STATES.YES, []


class ApiAlreadySavedErrorTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.create_app("config/testing.py")
        self._ctx = self.app.test_request_context()
        self._ctx.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self._ctx.pop()

    def test_mock_session_send_post_to_case_api(self):
        form = ContactForm()
        with patch("requests.Session.send", _mock_session_send), patch(
            "cla_public.apps.contact.views.get_case_ref_from_api", _mock_get_case_ref_from_api
        ):

            self.assertRaises(AlreadySavedApiError, post_to_case_api, form)

    def test_contact_on_valid_submit(self):
        with patch("cla_public.apps.contact.views.post_to_case_api", _mock_post_to_case_api), patch(
            "cla_public.apps.contact.views.get_case_ref_from_api", _mock_get_case_ref_from_api
        ), patch(
            "cla_public.apps.contact.views.post_to_eligibility_check_api", _mock_post_to_eligibility_check_api
        ), patch(
            "cla_public.apps.checker.session.post_to_is_eligible_api", _mock_post_to_is_eligible_api
        ):

            resp = Contact().on_valid_submit()

            self.assertEqual(resp.headers["Location"], "/result/confirmation")
            self.assertEqual(resp.status_code, 302)
