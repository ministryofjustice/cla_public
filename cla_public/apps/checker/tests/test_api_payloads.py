from mock import Mock, patch
import unittest

import flask
from werkzeug.datastructures import MultiDict

from cla_public import app
from cla_public.apps.checker.forms import YourBenefitsForm


def get_en_locale():
    return 'en'


class TestApiPayloads(unittest.TestCase):

    def setUp(self):
        self.patcher = patch('cla_public.libs.utils.get_locale', get_en_locale)
        self.patcher.start()
        self.app = app.create_app('config/testing.py')
        self._ctx = self.app.test_request_context()
        self._ctx.push()
        self.app = self.app.test_client()

    def tearDown(self):
        self.patcher.stop()

    def payload(self, form_class, form_data):
        form_class._get_translations = lambda args: None
        form = form_class(MultiDict(form_data), csrf_enabled=False)
        return form.api_payload()

    def test_your_benefits_form_passported(self):
        form_data = {'benefits': ['income_support']}
        payload = self.payload(YourBenefitsForm, form_data)
        self.assertTrue(payload['specific_benefits']['income_support'])
        self.assertTrue(payload['on_passported_benefits'])

    def test_your_benefits_form_multiple_passported(self):
        form_data = {'benefits': ['income_support', 'pension_credit']}
        payload = self.payload(YourBenefitsForm, form_data)
        self.assertTrue(payload['specific_benefits']['income_support'])
        self.assertTrue(payload['specific_benefits']['pension_credit'])
        self.assertTrue(payload['on_passported_benefits'])

    def test_your_benefits_form_no_passported(self):
        form_data = {'benefits': ['other-benefit']}
        payload = self.payload(YourBenefitsForm, form_data)
        are_false = lambda (benefit, selected): not selected
        self.assertTrue(
            all(map(are_false, payload['specific_benefits'].items())))
        self.assertFalse(payload['on_passported_benefits'])
