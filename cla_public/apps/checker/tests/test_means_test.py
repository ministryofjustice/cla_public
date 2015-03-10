from collections import defaultdict
from itertools import chain
import logging
import unittest

from flask import session
from werkzeug.datastructures import MultiDict

from cla_public.app import create_app
from cla_public.apps.checker import forms
from cla_public.apps.checker.constants import YES, NO
from cla_public.apps.checker.means_test import MeansTest
from cla_public.libs.money_interval import MoneyInterval


logging.getLogger('MARKDOWN').setLevel(logging.WARNING)


def post_money_interval(amount=None, interval='per_month'):
    return {
        'per_interval_value': amount,
        'interval_period': interval
    }


def form_payload(form_class, post_data):
    form_class = getattr(forms, form_class)
    form = form_class(MultiDict(post_data))
    return form.api_payload()


def about_you_payload(**kwargs):
    post_data = {
        'have_partner': NO,
        'in_dispute': NO,
        'on_benefits': NO,
        'have_children': NO,
        'num_children': '',
        'have_dependants': NO,
        'num_dependants': '',
        'have_savings': NO,
        'have_valuables': NO,
        'own_property': NO,
        'is_employed': NO,
        'partner_is_employed': NO,
        'is_self_employed': NO,
        'partner_is_self_employed': NO,
        'aged_60_or_over': NO}
    post_data.update(kwargs)
    return form_payload('AboutYouForm', post_data)


def flatten(dict_, prefix=[]):
    out = []
    for key, val in dict_.items():
        if isinstance(val, dict):
            out.extend(flatten(val, prefix + [key]))
        else:
            out.append(('-'.join(prefix + [key]),  val))
    return out


def properties_payload(*properties):
    prop = lambda (i, p): flatten(p, ['properties', str(i)])
    props = dict(chain(*map(prop, enumerate(properties))))
    print props
    return form_payload('PropertiesForm', props)


first_property = {
    'is_main_home': YES,
    'other_shareholders': NO,
    'property_value': '10,000.00',
    'mortgage_remaining': '9,000.00',
    'mortgage_payments': '800.00',
    'is_rented': NO,
    'rent_amount': post_money_interval(''),
    'in_dispute': NO
}


second_property = {
    'is_main_home': YES,
    'other_shareholders': NO,
    'property_value': '20,000.00',
    'mortgage_remaining': '10,000.00',
    'mortgage_payments': '700.00',
    'is_rented': NO,
    'rent_amount': post_money_interval(''),
    'in_dispute': NO
}


def rented(prop, rent):
    nprop = dict(prop)
    nprop['is_rented'] = YES
    nprop['rent_amount'] = rent
    return nprop


class TestMeansTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app('config/testing.py')
        self.client = self.app.test_client()
        self.app.test_request_context().push()
        with self.client.session_transaction() as session:
            session['foo'] = 'bar'

    def assertDictValues(self, dict_, expected=defaultdict(int)):
        for key, val in dict_.items():
            self.assertEqual(
                expected[key], val,
                '%s is %r, not %r' % (key, val, expected[key]))

    def assertZeroIncome(self, person, override={}):
        expected = set([
            'earnings', 'benefits', 'tax_credits', 'child_benefits',
            'other_income', 'self_employment_drawings', 'total',
            'maintenance_received', 'pension', 'self_employed'])
        self.assertSetEqual(
            expected, set(person['income'].keys()))

        expected = defaultdict(lambda: MoneyInterval(0))
        expected['total'] = 0
        expected['self_employed'] = NO
        expected.update(override)
        self.assertDictValues(person['income'], expected=expected)

    def assertZeroOutgoings(self, person, override={}):
        expected = set([
            'income_tax', 'mortgage', 'childcare', 'rent', 'maintenance',
            'national_insurance', 'criminal_legalaid_contributions'])
        self.assertSetEqual(
            expected, set(person['deductions'].keys()))

        expected = defaultdict(lambda: MoneyInterval(0))
        expected['criminal_legalaid_contributions'] = 0
        expected.update(override)
        self.assertDictValues(person['deductions'], expected=expected)

    def assertZeroSavings(self, person, override={}):
        expected = set([
            'credit_balance', 'investment_balance', 'asset_balance',
            'bank_balance', 'total'])
        self.assertSetEqual(
            expected, set(person['savings'].keys()))

        expected = defaultdict(int)
        expected.update(override)
        self.assertDictValues(person['savings'], expected=expected)

    def assertZeroFinances(self, person):
        expected = set(['income', 'savings', 'deductions'])
        self.assertSetEqual(expected, set(person.keys()))
        self.assertZeroIncome(person)
        self.assertZeroOutgoings(person)
        self.assertZeroSavings(person)

    def assertMeansTestInitialized(self, mt):
        self.assertEqual(0, mt['dependants_young'])
        self.assertEqual(0, mt['dependants_old'])
        self.assertEqual(NO, mt['on_passported_benefits'])
        self.assertEqual(NO, mt['on_nass_benefits'])
        self.assertEqual({}, mt['specific_benefits'])
        self.assertZeroFinances(mt['you'])
        self.assertZeroFinances(mt['partner'])

    def assertNullFinances(self, person):
        self.assertZeroIncome(person, override={
            'earnings': MoneyInterval(),
            'pension': MoneyInterval(),
            'maintenance_received': MoneyInterval(),
            'other_income': MoneyInterval()
        })
        self.assertZeroOutgoings(person, override={
            'income_tax': MoneyInterval(),
            'childcare': MoneyInterval(),
            'rent': MoneyInterval(),
            'maintenance': MoneyInterval(),
            'national_insurance': MoneyInterval(),
            'criminal_legalaid_contributions': None,
        })
        self.assertZeroSavings(person)

    def test_initialization(self):
        mt = MeansTest()
        self.assertMeansTestInitialized(mt)

    def test_set_problem_category(self):
        mt = MeansTest()
        mt.update(form_payload('ProblemForm', {'categories': 'debt'}))
        self.assertMeansTestInitialized(mt)
        self.assertEqual('debt', mt['category'])

    def test_reset_problem_category(self):
        mt = MeansTest()
        mt.update(form_payload('ProblemForm', {'categories': 'debt'}))
        mt.update(form_payload('ProblemForm', {'categories': 'family'}))
        self.assertMeansTestInitialized(mt)
        self.assertEqual('family', mt['category'])

    def test_about_you_all_no(self):
        mt = MeansTest()
        mt.update(form_payload('ProblemForm', {'categories': 'debt'}))
        mt.update(about_you_payload())

        self.assertEqual(NO, mt['on_passported_benefits'])
        self.assertEqual(NO, mt['on_nass_benefits'])
        self.assertEqual({}, mt['specific_benefits'])

        self.assertEqual(0, mt['dependants_young'])
        self.assertEqual(0, mt['dependants_old'])
        self.assertEqual(NO, mt['is_you_or_your_partner_over_60'])
        self.assertEqual(NO, mt['has_partner'])
        self.assertEqual(NO, mt['you']['income']['self_employed'])

        # fields that will need to be filled in must be set to null
        self.assertNullFinances(mt['you'])
        self.assertIsNone(mt['partner'])

        self.assertEqual([], mt['property_set'])

    def test_about_you_have_partner(self):
        mt = MeansTest()
        mt.update(form_payload('ProblemForm', {'categories': 'debt'}))
        mt.update(about_you_payload(have_partner=YES, in_dispute=NO))

        self.assertEqual(YES, mt['has_partner'])
        self.assertEqual(NO, mt['partner']['income']['self_employed'])

        payload = about_you_payload(
            have_partner=YES,
            in_dispute=NO,
            partner_is_self_employed=YES)
        mt.update(payload)

        self.assertEqual(YES, mt['partner']['income']['self_employed'])

        mt.update(about_you_payload(
            have_partner=YES,
            in_dispute=YES,
            partner_is_self_employed=YES))

        self.assertIsNone(mt['partner'])

        self.assertEqual([], mt['property_set'])

    def test_benefits_passported(self):
        mt = MeansTest()
        mt.update(form_payload('ProblemForm', {'categories': 'debt'}))
        mt.update(about_you_payload(
            on_benefits=YES))
        mt.update(form_payload('YourBenefitsForm', {
            'benefits': 'income_support'}))

        self.assertTrue(mt['on_passported_benefits'])
        expected = {
            'income_support': True,
            'job_seekers_allowance': False,
            'pension_credit': False,
            'universal_credit': False,
            'employment_support': False
        }
        self.assertEqual(expected, mt['specific_benefits'])

        self.assertZeroIncome(mt['you'])
        self.assertZeroOutgoings(mt['you'])
        self.assertZeroSavings(mt['you'])
        self.assertIsNone(mt['partner'])

        self.assertEqual([], mt['property_set'])

    def test_benefits_not_passported(self):
        mt = MeansTest()
        mt.update(form_payload('ProblemForm', {'categories': 'debt'}))
        mt.update(about_you_payload(on_benefits=YES))
        mt.update(form_payload('YourBenefitsForm', {
            'benefits': 'other-benefit'}))

        self.assertFalse(mt['on_passported_benefits'])
        expected = {
            'income_support': False,
            'job_seekers_allowance': False,
            'pension_credit': False,
            'universal_credit': False,
            'employment_support': False
        }
        self.assertEqual(expected, mt['specific_benefits'])

        self.assertNullFinances(mt['you'])
        self.assertIsNone(mt['partner'])

        self.assertEqual([], mt['property_set'])

    def test_property(self):
        mt = MeansTest()
        mt.update(form_payload('ProblemForm', {'categories': 'debt'}))
        mt.update(about_you_payload(own_property=YES))
        mt.update(properties_payload(first_property))

        self.assertZeroIncome(mt['you'], override={
            'earnings': MoneyInterval(),
            'pension': MoneyInterval(),
            'maintenance_received': MoneyInterval()
        })
        self.assertZeroOutgoings(mt['you'], override={
            'income_tax': MoneyInterval(),
            'childcare': MoneyInterval(),
            'rent': MoneyInterval(),
            'maintenance': MoneyInterval(),
            'national_insurance': MoneyInterval(),
            'criminal_legalaid_contributions': None,
            'mortgage': MoneyInterval('800.00', 'per_month')
        })
        self.assertZeroSavings(mt['you'])
        self.assertIsNone(mt['partner'])

        expected = [{
            'value': 1000000,
            'mortgage_left': 900000,
            'share': 100,
            'disputed': NO,
            'rent': MoneyInterval(0),
            'main': YES
        }]
        self.assertDictEqual(expected[0], mt['property_set'][0])

    def test_multiple_property(self):
        mt = MeansTest()
        mt.update(form_payload('ProblemForm', {'categories': 'debt'}))
        mt.update(about_you_payload(own_property=YES))
        mt.update(properties_payload(first_property, second_property))

        self.assertZeroIncome(mt['you'], override={
            'earnings': MoneyInterval(),
            'pension': MoneyInterval(),
            'maintenance_received': MoneyInterval()
        })
        self.assertZeroOutgoings(mt['you'], override={
            'income_tax': MoneyInterval(),
            'childcare': MoneyInterval(),
            'rent': MoneyInterval(),
            'maintenance': MoneyInterval(),
            'national_insurance': MoneyInterval(),
            'criminal_legalaid_contributions': None,
            'mortgage': MoneyInterval('1500.00', 'per_month')
        })
        self.assertZeroSavings(mt['you'])
        self.assertIsNone(mt['partner'])

        expected = [{
            'value': 1000000,
            'mortgage_left': 900000,
            'share': 100,
            'disputed': NO,
            'rent': MoneyInterval(0),
            'main': YES
        }, {
            'value': 2000000,
            'mortgage_left': 1000000,
            'share': 100,
            'disputed': NO,
            'rent': MoneyInterval(0),
            'main': YES
        }]
        self.assertDictEqual(expected[0], mt['property_set'][0])
        self.assertDictEqual(expected[1], mt['property_set'][1])

    def test_rent(self):
        mt = MeansTest()
        mt.update(form_payload('ProblemForm', {'categories': 'debt'}))

        mt.update(about_you_payload(own_property=YES))
        session['AboutYouForm'] = {
            'have_partner': NO,
            'own_property': YES}

        prop = rented(first_property, post_money_interval('100.00'))
        payload = properties_payload(prop)
        print payload
        mt.update(payload)
        session['PropertiesForm'] = {
            'properties': [prop]}

        self.assertZeroIncome(mt['you'], override={
            'earnings': MoneyInterval(),
            'pension': MoneyInterval(),
            'maintenance_received': MoneyInterval(),
            'other_income': MoneyInterval('100.00')
        })

    def test_multiple_rents(self):
        mt = MeansTest()
        mt.update(form_payload('ProblemForm', {'categories': 'debt'}))
        mt.update(about_you_payload(own_property=YES))
        session['AboutYouForm'] = {
            'have_partner': NO,
            'own_property': YES}

        prop1 = rented(first_property, post_money_interval('100.00'))
        prop2 = rented(second_property, post_money_interval('50.00'))
        mt.update(properties_payload(prop1, prop2))
        session['PropertiesForm'] = {
            'properties': [prop1, prop2]}

        self.assertZeroIncome(mt['you'], override={
            'earnings': MoneyInterval(),
            'pension': MoneyInterval(),
            'maintenance_received': MoneyInterval(),
            'other_income': MoneyInterval('150.00')
        })
