# -*- coding: utf-8 -*-
import datetime
from flask import session
from mock import Mock, patch
import unittest
import pytz
from werkzeug.datastructures import MultiDict

from cla_public import app
from cla_public.apps.checker.constants import NO, YES
from cla_public.apps.callmeback.forms import CallMeBackForm
from cla_public.apps.checker.forms import YourBenefitsForm, AboutYouForm, \
    PropertiesForm, SavingsForm, TaxCreditsForm, IncomeFieldForm, \
    IncomeForm, OutgoingsForm


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

    def flatten_dict(self, field_name, data_dict):
        return {'%s-%s' % (field_name, key): val for key, val in data_dict.items()}

    def flatten_list_of_dicts(self, field_name, data_list):
        return {'%s-%s-%s' % (field_name, num, key): val for num, d in enumerate(data_list) for key, val in d.items()}

    def merge_money_intervals(self, form_data, form_mi_data):
        for field_name, money_interval_dict in form_mi_data.items():
            form_data.update(self.flatten_dict(field_name, money_interval_dict))
        return form_data

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
        rent_amount = {
            'per_interval_value': '30',
            'interval_period': 'per_week'
        }

        property_one = {
            'is_main_home': YES,
            'other_shareholders': NO,
            'property_value': '100',
            'mortgage_remaining': '99',
            'mortgage_payments': '1',
            'is_rented': YES,
            'in_dispute': NO
        }

        property_one.update(self.flatten_dict('rent_amount', rent_amount))

        properties = [
            property_one,
        ]

        # need to convert FieldList to flat fields to load in to form
        form_data = self.flatten_list_of_dicts('properties', properties)

        payload = self.payload(PropertiesForm, form_data)

        self.assertEqual(len(payload['property_set']), 1)

        self.assertEqual(payload['property_set'][0]['value'], 10000)
        self.assertEqual(payload['property_set'][0]['mortgage_left'], 9900)
        self.assertEqual(payload['property_set'][0]['share'], 100)
        self.assertEqual(payload['property_set'][0]['disputed'], NO)
        self.assertEqual(payload['property_set'][0]['rent']['per_interval_value'], 3000)
        self.assertEqual(payload['property_set'][0]['rent']['interval_period'], 'per_week')
        self.assertEqual(payload['property_set'][0]['main'], YES)

    def test_saving_form(self):
        session['AboutYouForm_have_savings'] = YES
        session['AboutYouForm_have_valuables'] = YES
        form_data = {
            'savings': '100',
            'investments': '100',
            'valuables': '500',
        }

        payload = self.payload(SavingsForm, form_data)

        self.assertEqual(payload['you']['savings']['bank_balance'], 10000)
        self.assertEqual(payload['you']['savings']['investment_balance'], 10000)
        self.assertEqual(payload['you']['savings']['asset_balance'], 50000)

        session['AboutYouForm_have_valuables'] = NO
        payload = self.payload(SavingsForm, form_data)

        self.assertEqual(payload['you']['savings']['asset_balance'], 0,
                         msg=u'Should be 0 if user selected no valuables')

        session['AboutYouForm_have_savings'] = NO
        session['AboutYouForm_have_valuables'] = YES
        payload = self.payload(SavingsForm, form_data)

        self.assertEqual(payload['you']['savings']['bank_balance'], 0)
        self.assertEqual(payload['you']['savings']['investment_balance'], 0)

    def test_tax_credit_form(self):
        form_mi_data = {
            'child_benefit': {
                'per_interval_value': '21',
                'interval_period': 'per_week'
            },
            'child_tax_credit': {
                'per_interval_value': '32',
                'interval_period': 'per_week'
            },
            'total_other_benefit': {
                'per_interval_value': '43',
                'interval_period': 'per_week'
            },
        }

        form_data = {
            'benefits': 'asylum-support',
            'other_benefits': YES,
        }

        form_data = self.merge_money_intervals(form_data, form_mi_data)

        payload = self.payload(TaxCreditsForm, form_data)

        self.assertEqual(payload['on_nass_benefits'], True)
        self.assertEqual(payload['you']['income']['child_benefits']['per_interval_value'], 2100)
        self.assertEqual(payload['you']['income']['tax_credits']['per_interval_value'], 3200)
        self.assertEqual(payload['you']['income']['benefits']['per_interval_value'], 4300)

    def test_income_form(self):
        form_mi_data = {
            'earnings': {
                'per_interval_value': '1',
                'interval_period': 'per_week'
            },
            'income_tax': {
                'per_interval_value': '2',
                'interval_period': 'per_week'
            },
            'national_insurance': {
                'per_interval_value': '3',
                'interval_period': 'per_week'
            },
            'working_tax_credit': {
                'per_interval_value': '4',
                'interval_period': 'per_month'
            },
            'maintenance': {
                'per_interval_value': '5',
                'interval_period': 'per_week'
            },
            'pension': {
                'per_interval_value': '6',
                'interval_period': 'per_week'
            },
            'other_income': {
                'per_interval_value': '7',
                'interval_period': 'per_week'
            },
        }

        form_data = self.merge_money_intervals({}, form_mi_data)

        payload = self.payload(IncomeFieldForm, form_data)

        self.assertEqual(payload['income']['earnings']['per_interval_value'], 100)
        self.assertEqual(payload['income']['earnings']['interval_period'], 'per_week')
        self.assertEqual(payload['income']['self_employment_drawings']['per_interval_value'], 0)
        self.assertEqual(payload['income']['tax_credits']['per_interval_value'], 400)
        self.assertEqual(payload['income']['tax_credits']['interval_period'], 'per_month')
        self.assertEqual(payload['income']['maintenance_received']['per_interval_value'], 500)
        self.assertEqual(payload['income']['pension']['per_interval_value'], 600)
        self.assertEqual(payload['income']['other_income']['per_interval_value'], 700)

        self.assertEqual(payload['deductions']['income_tax']['per_interval_value'], 200)
        self.assertEqual(payload['deductions']['national_insurance']['per_interval_value'], 300)

    def test_income_and_tax_form(self):
        session['AboutYouForm_have_partner'] = YES
        session['AboutYouForm_in_dispute'] = NO

        payload = self.payload(IncomeForm, {})

        self.assertIn('you', payload)
        self.assertIn('partner', payload)

    def test_outgoing_form(self):
        form_mi_data = {
            'rent': {
                'per_interval_value': '27',
                'interval_period': 'per_month'
            },
            'maintenance': {
                'per_interval_value': '38',
                'interval_period': 'per_week'
            },
            'childcare': {
                'per_interval_value': '49',
                'interval_period': 'per_week'
            },
        }

        form_data = {
            'income_contribution': '23',
        }

        form_data = self.merge_money_intervals(form_data, form_mi_data)

        payload = self.payload(OutgoingsForm, form_data)

        self.assertEqual(payload['you']['deductions']['rent']['per_interval_value'], 2700)
        self.assertEqual(payload['you']['deductions']['rent']['interval_period'], 'per_month')
        self.assertEqual(payload['you']['deductions']['maintenance']['per_interval_value'], 3800)
        self.assertEqual(payload['you']['deductions']['maintenance']['interval_period'], 'per_week')
        self.assertEqual(payload['you']['deductions']['criminal_legalaid_contributions'], 2300)
        self.assertEqual(payload['you']['deductions']['childcare']['per_interval_value'], 4900)
        self.assertEqual(payload['you']['deductions']['childcare']['interval_period'], 'per_week')

    def test_application_form(self):
        adaptations_data = {
            'bsl_webcam': YES,
            'minicom': YES,
            'text_relay': YES,
            'welsh': YES,
            'is_other_language': YES,
            'other_language': YES,
            'is_other_adaptation': YES,
            'other_adaptation': 'other',
        }

        form_data = {
            'full_name': 'Full Name',
            'contact_number': '000000000',
            'safe_to_contact': YES,
            'post_code': 'POSTCODE',
            'address': '21 Jump Street',
            'extra_notes': 'Extra notes',

            'specific_day': 'today',
            'time_today': '1945',
            'day': '',
            'time_in_day': '',
        }

        form_data.update(self.flatten_dict('adaptations', adaptations_data))

        payload = self.payload(CallMeBackForm, form_data)

        self.assertEqual(payload['personal_details']['full_name'], 'Full Name')
        self.assertEqual(payload['personal_details']['postcode'], 'POSTCODE')
        self.assertEqual(payload['personal_details']['mobile_phone'], '000000000')
        self.assertEqual(payload['personal_details']['street'], '21 Jump Street')
        self.assertEqual(payload['personal_details']['safe_to_contact'], YES)

        self.assertEqual(payload['adaptation_details']['bsl_webcam'], True)
        self.assertEqual(payload['adaptation_details']['minicom'], True)
        self.assertEqual(payload['adaptation_details']['text_relay'], True)
        self.assertEqual(payload['adaptation_details']['language'], 'WELSH')
        self.assertEqual(payload['adaptation_details']['notes'], 'other')

        time = datetime.datetime.combine(datetime.date.today(), datetime.time(19, 45))
        self.assertEqual(payload['requires_action_at'], time.replace(tzinfo=pytz.utc).isoformat())

