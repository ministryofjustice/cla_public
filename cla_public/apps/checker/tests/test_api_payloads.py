from mock import Mock, patch
import unittest

import flask
from werkzeug.datastructures import MultiDict

from cla_public import app
from cla_public.apps.checker.constants import NO, YES
from cla_public.apps.checker.fields import MoneyIntervalForm
from cla_public.apps.checker.forms import YourBenefitsForm, AboutYouForm, \
    PropertiesForm, PropertyForm


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

    def form(self, form_class, form_data):
        form_class._get_translations = lambda args: None
        return form_class(MultiDict(form_data), csrf_enabled=False)

    def payload(self, form_class, form_data):
        form = self.form(form_class, form_data)
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

    def test_about_you_form(self):
        form_data = {
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
        }

        payload = self.payload(AboutYouForm, form_data)
        self.assertEqual(payload['partner']['income']['self_employed'], YES)

        self.assertEqual(payload['dependants_young'], 0)
        self.assertEqual(payload['dependants_old'], 0)
        self.assertEqual(payload['is_you_or_your_partner_over_60'], NO)
        self.assertEqual(payload['has_partner'], YES)
        self.assertEqual(payload['you']['income']['self_employed'], NO)

        form_data['have_partner'] = NO
        payload = self.payload(AboutYouForm, form_data)
        self.assertNotIn('partner', payload)

        form_data.update({
            'have_dependants': YES,
            'num_dependants': 2,
            'have_children': YES,
            'num_children': 3,
        })
        payload = self.payload(AboutYouForm, form_data)
        self.assertEqual(payload['dependants_young'], 3)
        self.assertEqual(payload['dependants_old'], 2)

        form_data.update({
            'have_dependants': NO,
            'have_children': NO,
        })
        payload = self.payload(AboutYouForm, form_data)
        self.assertEqual(payload['dependants_young'], 0)
        self.assertEqual(payload['dependants_old'], 0)

    def test_property_form(self):
        properties = [
            {
                'is_main_home': YES,
                'other_shareholders': NO,
                'property_value': '100',
                'mortgage_remaining': '99',
                'mortgage_payments': '1',
                'is_rented': NO,
                'rent_amount': {
                    'per_interval_value': '30',
                    'interval_period': 'per_week'
                },
                'in_dispute': NO
            },
        ]

        # need to convert FieldList to flat fields to load in to form
        form_data = {'properties-%s-%s' % (num, key): val for num, p in enumerate(properties) for key, val in p.items()}

        payload = self.payload(PropertiesForm, form_data)

        self.assertEqual(len(payload['property_set']), 1)

        self.assertEqual(payload['property_set'][0]['value'], 10000)
        self.assertEqual(payload['property_set'][0]['mortgage_left'], 9900)
        self.assertEqual(payload['property_set'][0]['share'], 100)
        self.assertEqual(payload['property_set'][0]['disputed'], NO)
        self.assertEqual(payload['property_set'][0]['rent']['per_interval_value'], 0)
        self.assertEqual(payload['property_set'][0]['rent']['interval_period'], 'per_month')
        self.assertEqual(payload['property_set'][0]['main'], YES)
