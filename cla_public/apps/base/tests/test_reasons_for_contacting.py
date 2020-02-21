from random import choice
import unittest

from flask import url_for
from werkzeug.datastructures import MultiDict

from cla_public.apps.base.constants import REASONS_FOR_CONTACTING_CHOICES
from cla_public.apps.base.forms import ReasonsForContactingForm
from cla_public.apps.checker.api import post_reasons_for_contacting
from cla_public.apps.base.tests import FlaskAppTestCase


class ReasonsForContactingTestCase(FlaskAppTestCase):
    def setUp(self):
        super(ReasonsForContactingTestCase, self).setUp()
        self.client = self.app.test_client()

    @unittest.skip("Skip this tests until request is mocked. These were ignored before with nosetests")
    def test_submission(self):
        income_page_url = url_for("checker.wizard", step="income")
        random_reason = str(choice(REASONS_FOR_CONTACTING_CHOICES)[0])

        api_payload = ReasonsForContactingForm(
            formdata=MultiDict(
                {"referrer": income_page_url, "other_reasons": "other reasons", "reasons": [random_reason]}
            )
        ).api_payload()

        response = post_reasons_for_contacting(payload=api_payload)
        self.assertIsInstance(response, dict, "Reason for contacting response not a dict")
        self.assertDictContainsSubset(
            {"referrer": income_page_url, "other_reasons": "other reasons", "reasons": [{"category": random_reason}]},
            response,
        )
        self.assertTrue(response["reference"], "Reason for contacting not given a reference")
