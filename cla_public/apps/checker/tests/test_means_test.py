from collections import defaultdict
import logging
import unittest

from werkzeug.datastructures import MultiDict

from cla_public.app import create_app
from cla_public.apps.checker import forms
from cla_public.apps.checker.constants import YES, NO
from cla_public.apps.checker.means_test import MeansTest
from cla_public.libs.money_interval import MoneyInterval


logging.getLogger('MARKDOWN').setLevel(logging.WARNING)


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


class TestMeansTest(unittest.TestCase):

    def setUp(self):
        app = create_app('config/testing.py')
        self.client = app.test_client()
        app.test_request_context().push()

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
            'other_income': MoneyInterval(),
            'pension': MoneyInterval(),
            'maintenance_received': MoneyInterval()
        })
        self.assertZeroOutgoings(person, override={
            'income_tax': MoneyInterval(),
            'childcare': MoneyInterval(),
            'national_insurance': MoneyInterval(),
            'rent': MoneyInterval(),
            'maintenance': MoneyInterval(),
            'criminal_legalaid_contributions': None
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
        self.assertZeroIncome(mt['you'], override={
            'earnings': MoneyInterval(),
            'pension': MoneyInterval(),
            'maintenance_received': MoneyInterval(),
            'other_income': MoneyInterval()
        })
        self.assertZeroOutgoings(mt['you'], override={
            'income_tax': MoneyInterval(),
            'childcare': MoneyInterval(),
            'rent': MoneyInterval(),
            'maintenance': MoneyInterval(),
            'national_insurance': MoneyInterval(),
            'criminal_legalaid_contributions': None,
        })
        self.assertZeroSavings(mt['you'])
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
