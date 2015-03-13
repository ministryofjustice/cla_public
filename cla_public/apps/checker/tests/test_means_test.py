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
        'num_children': '0',
        'have_dependants': NO,
        'num_dependants': '0',
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
            session.clear()

    def assertDictValues(self, expected, actual):
        for key, val in actual.items():
            self.assertEqual(
                expected[key], val,
                '%s is %r, not %r' % (key, val, expected[key]))

    def assertIncome(self, income, default=None, **override):
        expected = set([
            'earnings', 'benefits', 'tax_credits', 'child_benefits',
            'other_income', 'self_employment_drawings', 'total',
            'maintenance_received', 'pension', 'self_employed'])
        self.assertSetEqual(
            expected, set(income.keys()))

        expected = defaultdict(lambda: default)
        expected['total'] = 0
        expected['self_employed'] = NO
        expected.update(override)
        self.assertDictValues(expected, income)

    def assertOutgoings(self, outgoings, default=None, **override):
        expected = set([
            'income_tax', 'mortgage', 'childcare', 'rent', 'maintenance',
            'national_insurance', 'criminal_legalaid_contributions'])
        self.assertSetEqual(
            expected, set(outgoings.keys()))

        expected = defaultdict(lambda: default)
        expected['criminal_legalaid_contributions'] = 0
        expected.update(override)
        self.assertDictValues(expected, outgoings)

    def assertSavings(self, savings, default=None, **override):
        expected = set([
            'credit_balance', 'investment_balance', 'asset_balance',
            'bank_balance', 'total'])
        self.assertSetEqual(
            expected, set(savings.keys()))

        expected = defaultdict(lambda: default)
        expected.update(override)
        self.assertDictValues(expected, savings)

    def assertZeroFinances(self, person):
        expected = set(['income', 'savings', 'deductions'])
        self.assertSetEqual(expected, set(person.keys()))
        self.assertIncome(person['income'], default=MoneyInterval(0))
        self.assertOutgoings(person['deductions'], default=MoneyInterval(0))
        self.assertSavings(person['savings'], default=0)

    def assertMeansTestInitialized(self, mt):
        self.assertEqual(0, mt['dependants_young'])
        self.assertEqual(0, mt['dependants_old'])
        self.assertEqual(NO, mt['on_passported_benefits'])
        self.assertEqual(NO, mt['on_nass_benefits'])
        self.assertEqual({}, mt['specific_benefits'])
        self.assertZeroFinances(mt['you'])
        self.assertZeroFinances(mt['partner'])

    def assertNullFinances(self, person):
        self.assertIncome(
            person['income'],
            default=MoneyInterval(0),
            earnings=MoneyInterval(),
            pension=MoneyInterval(),
            maintenance_received=MoneyInterval(),
            other_income=MoneyInterval()
        )
        self.assertOutgoings(
            person['deductions'],
            default=MoneyInterval(),
            mortgage=MoneyInterval(0),
            criminal_legalaid_contributions=None
        )
        self.assertSavings(person['savings'], default=0)

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

        self.assertIncome(mt['you']['income'], default=MoneyInterval(0))
        self.assertOutgoings(mt['you']['deductions'], default=MoneyInterval(0))
        self.assertSavings(mt['you']['savings'], default=0)
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

        self.assertIncome(
            mt['you']['income'],
            default=MoneyInterval(0),
            earnings=MoneyInterval(),
            pension=MoneyInterval(),
            maintenance_received=MoneyInterval()
        )
        self.assertOutgoings(
            mt['you']['deductions'],
            default=MoneyInterval(),
            criminal_legalaid_contributions=None,
            mortgage=MoneyInterval('800.00', 'per_month')
        )
        self.assertSavings(mt['you']['savings'], default=0)
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

        self.assertIncome(
            mt['you']['income'],
            default=MoneyInterval(0),
            earnings=MoneyInterval(),
            pension=MoneyInterval(),
            maintenance_received=MoneyInterval()
        )
        self.assertOutgoings(
            mt['you']['deductions'],
            default=MoneyInterval(),
            criminal_legalaid_contributions=None,
            mortgage=MoneyInterval('1500.00', 'per_month')
        )
        self.assertSavings(mt['you']['savings'], default=0)
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
        mt.update(properties_payload(prop))
        session['PropertiesForm'] = {
            'properties': [prop]}

        self.assertIncome(
            mt['you']['income'],
            default=MoneyInterval(0),
            earnings=MoneyInterval(),
            pension=MoneyInterval(),
            maintenance_received=MoneyInterval(),
            other_income=MoneyInterval('100.00')
        )

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

        self.assertIncome(
            mt['you']['income'],
            default=MoneyInterval(0),
            earnings=MoneyInterval(),
            pension=MoneyInterval(),
            maintenance_received=MoneyInterval(),
            other_income=MoneyInterval('150.00')
        )

    def test_savings(self):
        mt = MeansTest()
        mt.update(form_payload('ProblemForm', {'categories': 'debt'}))
        mt.update(about_you_payload(have_savings=YES, have_valuables=YES))
        session['AboutYouForm'] = {
            'have_savings': YES,
            'have_valuables': YES}

        mt.update(form_payload('SavingsForm', {
            'savings': '1,000.00',
            'investments': '0.00',
            'valuables': '500.00'}))

        self.assertEqual(100000, mt['you']['savings']['bank_balance'])
        self.assertEqual(0, mt['you']['savings']['investment_balance'])
        self.assertEqual(50000, mt['you']['savings']['asset_balance'])

    def test_tax_credits(self):
        mt = MeansTest()
        mt.update(form_payload('ProblemForm', {'categories': 'debt'}))
        mt.update(about_you_payload())
        mt.update(form_payload('TaxCreditsForm', dict(flatten({
            'child_benefit': post_money_interval('1', 'per_week'),
            'child_tax_credit': post_money_interval('2', 'per_week'),
            'benefits': [],
            'other_benefits': YES,
            'total_other_benefit': post_money_interval('3', 'per_week')
        }))))

        self.assertFalse(mt['on_nass_benefits'])
        self.assertEqual(
            MoneyInterval(100, 'per_week'),
            mt['you']['income']['child_benefits'])
        self.assertEqual(
            MoneyInterval(200, 'per_week'),
            mt['you']['income']['tax_credits'])
        self.assertEqual(
            MoneyInterval(300, 'per_week'),
            mt['you']['income']['benefits'])

    def test_nass_benefits(self):
        mt = MeansTest()
        mt.update(form_payload('TaxCreditsForm', dict(flatten({
            'child_benefit': post_money_interval('0'),
            'child_tax_credit': post_money_interval('0'),
            'benefits': ['asylum-support'],
            'other_benefits': NO,
            'total_other_benefit': post_money_interval('0')}))))

        self.assertTrue(mt['on_nass_benefits'])

    def test_child_tax_credits_and_working_tax_credits(self):
        session['TaxCreditsForm'] = {
            'child_tax_credit': MoneyInterval(1000, 'per_week')}

        mt = MeansTest()
        mt.update(form_payload('IncomeForm', dict(flatten({
            'your_income': {
                'earnings': post_money_interval('0'),
                'income_tax': post_money_interval('0'),
                'national_insurance': post_money_interval('0'),
                'working_tax_credit': post_money_interval('10.00'),
                'maintenance': post_money_interval('0'),
                'pension': post_money_interval('0'),
                'other_income': post_money_interval('0')
            }
        }))))

        self.assertEqual(
            MoneyInterval(5333),
            mt['you']['income']['tax_credits'])

    def test_income_self_employed(self):
        session['AboutYouForm'] = {'is_self_employed': YES}

        mt = MeansTest()
        mt.update(form_payload('IncomeForm', dict(flatten({
            'your_income': {
                'earnings': post_money_interval('1'),
                'income_tax': post_money_interval('2'),
                'national_insurance': post_money_interval('3'),
                'working_tax_credit': post_money_interval('4'),
                'maintenance': post_money_interval('5'),
                'pension': post_money_interval('6'),
                'other_income': post_money_interval('7')
            }}))))

        self.assertEqual(MoneyInterval(0), mt['you']['income']['earnings'])
        self.assertEqual(
            MoneyInterval(100),
            mt['you']['income']['self_employment_drawings'])
        self.assertEqual(
            MoneyInterval(200),
            mt['you']['deductions']['income_tax'])
        self.assertEqual(
            MoneyInterval(300),
            mt['you']['deductions']['national_insurance'])
        self.assertEqual(
            MoneyInterval(400),
            mt['you']['income']['tax_credits'])
        self.assertEqual(
            MoneyInterval(500),
            mt['you']['income']['maintenance_received'])
        self.assertEqual(
            MoneyInterval(600),
            mt['you']['income']['pension'])
        self.assertEqual(
            MoneyInterval(700),
            mt['you']['income']['other_income'])

        def test_partner_income(self):
            session['AboutYouForm'] = {
                'have_partner': YES,
                'partner_is_employed': YES}

            mt = MeansTest()
            mt.update(form_payload('IncomeForm', dict(flatten({
                'your_income': {
                    'earnings': post_money_interval('0'),
                    'income_tax': post_money_interval('0'),
                    'national_insurance': post_money_interval('0'),
                    'working_tax_credit': post_money_interval('0'),
                    'maintenance': post_money_interval('0'),
                    'pension': post_money_interval('0'),
                    'other_income': post_money_interval('0')
                },
                'partner_income': {
                    'earnings': post_money_interval('1'),
                    'income_tax': post_money_interval('2'),
                    'national_insurance': post_money_interval('3'),
                    'working_tax_credit': post_money_interval('4'),
                    'maintenance': post_money_interval('5'),
                    'pension': post_money_interval('6'),
                    'other_income': post_money_interval('7')
                }
            }))))

            self.assertEqual(
                MoneyInterval(100),
                mt['partner']['income']['earnings'])
            self.assertEqual(
                MoneyInterval(200),
                mt['partner']['deductions']['income_tax'])
            self.assertEqual(
                MoneyInterval(300),
                mt['partner']['deductions']['national_insurance'])
            self.assertEqual(
                MoneyInterval(400),
                mt['partner']['income']['tax_credits'])
            self.assertEqual(
                MoneyInterval(500),
                mt['partner']['income']['maintenance_received'])
            self.assertEqual(
                MoneyInterval(600),
                mt['partner']['income']['pension'])
            self.assertEqual(
                MoneyInterval(700),
                mt['partner']['income']['other_income'])
