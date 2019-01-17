from collections import defaultdict
from itertools import chain
import logging
import unittest

from flask import session

from cla_public.app import create_app
from cla_public.apps.checker.constants import YES, NO
from cla_public.apps.checker.means_test import MeansTest
from cla_public.libs.money_interval import MoneyInterval

logging.getLogger("MARKDOWN").setLevel(logging.WARNING)


def post_money_interval(amount=None, interval="per_month"):
    return {"per_interval_value": amount, "interval_period": interval}


def about_you_post_data(**kwargs):
    post_data = {
        "have_partner": NO,
        "in_dispute": NO,
        "on_benefits": NO,
        "have_children": NO,
        "num_children": "0",
        "have_dependants": NO,
        "num_dependants": "0",
        "have_savings": NO,
        "have_valuables": NO,
        "own_property": NO,
        "is_employed": NO,
        "partner_is_employed": NO,
        "is_self_employed": NO,
        "partner_is_self_employed": NO,
        "aged_60_or_over": NO,
    }
    post_data.update(kwargs)
    return post_data


def flatten(dict_, prefix=[]):
    out = []
    for key, val in dict_.items():
        if isinstance(val, dict):
            out.extend(flatten(val, prefix + [key]))
        else:
            out.append(("-".join(prefix + [key]), val))
    return out


def flatten_prop(prop):
    return flatten(prop[1], ["properties", str(prop[0])])


def properties_post_data(*properties):
    props = dict(chain(*map(flatten_prop, enumerate(properties))))
    return props


first_property = {
    "is_main_home": YES,
    "other_shareholders": NO,
    "property_value": "10,000.00",
    "mortgage_remaining": "9,000.00",
    "mortgage_payments": "800.00",
    "is_rented": NO,
    "rent_amount": post_money_interval(""),
    "in_dispute": NO,
}

second_property = {
    "is_main_home": YES,
    "other_shareholders": NO,
    "property_value": "20,000.00",
    "mortgage_remaining": "10,000.00",
    "mortgage_payments": "700.00",
    "is_rented": NO,
    "rent_amount": post_money_interval(""),
    "in_dispute": NO,
}


def rented(prop, rent):
    nprop = dict(prop)
    nprop["is_rented"] = YES
    nprop["rent_amount"] = rent
    return nprop


def update_session(form, **kwargs):
    session.checker[form] = session.checker.get(form, {})
    session.checker[form].update(**kwargs)


class TestMeansTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app("config/testing.py")
        self.client = self.app.test_client()
        self.app.test_request_context().push()
        session.clear()

    def assertDictValues(self, expected, actual):
        for key, val in actual.items():
            self.assertEqual(expected[key], val, "%s is %r, not %r" % (key, val, expected[key]))

    def assertIncome(self, income, default=None, **override):
        expected = set(
            [
                "earnings",
                "benefits",
                "tax_credits",
                "child_benefits",
                "other_income",
                "self_employment_drawings",
                "maintenance_received",
                "pension",
                "self_employed",
            ]
        )
        self.assertSetEqual(expected, set(income.keys()))

        expected = defaultdict(lambda: default)
        expected["total"] = 0
        expected["self_employed"] = NO
        expected.update(override)
        self.assertDictValues(expected, income)

    def assertOutgoings(self, outgoings, default=None, **override):
        expected = set(
            [
                "income_tax",
                "mortgage",
                "childcare",
                "rent",
                "maintenance",
                "national_insurance",
                "criminal_legalaid_contributions",
            ]
        )
        self.assertSetEqual(expected, set(outgoings.keys()))

        expected = defaultdict(lambda: default)
        expected["criminal_legalaid_contributions"] = 0
        expected.update(override)
        self.assertDictValues(expected, outgoings)

    def assertSavings(self, savings, default=None, **override):
        expected = set(["credit_balance", "investment_balance", "asset_balance", "bank_balance"])
        self.assertSetEqual(expected, set(savings.keys()))

        expected = defaultdict(lambda: default)
        expected.update(override)
        self.assertDictValues(expected, savings)

    def assertMeansTestInitialized(self, mt, partner=False):
        self.assertEqual(0, mt["dependants_young"])
        self.assertEqual(0, mt["dependants_old"])
        self.assertEqual(NO, mt["on_passported_benefits"])
        self.assertEqual(NO, mt["on_nass_benefits"])
        self.assertEqual({}, mt["specific_benefits"])
        expected = set(["income", "savings", "deductions"])
        self.assertSetEqual(expected, set(mt["you"].keys()))
        self.assertIncome(mt["you"]["income"], default=MoneyInterval(0))
        self.assertOutgoings(mt["you"]["deductions"], default=MoneyInterval(0))
        self.assertSavings(mt["you"]["savings"], default=0)
        if partner:
            self.assertIncome(mt["partner"]["income"], default=MoneyInterval(0))
            self.assertOutgoings(mt["partner"]["deductions"], default=MoneyInterval(0))
            self.assertSavings(mt["partner"]["savings"], default=0)

    def assertNullFinances(self, person, income_overrides={}, outgoings_overrides={}, savings_overrides={}):
        self.assertIncome(
            person["income"],
            default=MoneyInterval(0),
            earnings=MoneyInterval(),
            pension=MoneyInterval(),
            maintenance_received=MoneyInterval(),
            other_income=MoneyInterval(),
            **income_overrides
        )
        self.assertOutgoings(
            person["deductions"],
            default=MoneyInterval(),
            mortgage=MoneyInterval(0),
            criminal_legalaid_contributions=None,
            **outgoings_overrides
        )
        self.assertSavings(person["savings"], default=0, **savings_overrides)

    def test_initialization(self):
        mt = MeansTest()
        self.assertMeansTestInitialized(mt)

        update_session("AboutYouForm", have_partner=YES, in_dispute=NO)

        mt = MeansTest()
        self.assertMeansTestInitialized(mt)

    def test_about_you_all_no(self):
        update_session("AboutYouForm", is_employed=YES, have_children=YES)

        session.checker["category"] = "debt"
        mt = MeansTest()
        mt.update_from_form("AboutYouForm", about_you_post_data(is_employed=YES))

        self.assertEqual(NO, mt["on_passported_benefits"])
        self.assertEqual(NO, mt["on_nass_benefits"])
        self.assertEqual({}, mt["specific_benefits"])

        self.assertEqual(0, mt["dependants_young"])
        self.assertEqual(0, mt["dependants_old"])
        self.assertEqual(NO, mt["is_you_or_your_partner_over_60"])
        self.assertEqual(NO, mt["has_partner"])
        self.assertEqual(NO, mt["you"]["income"]["self_employed"])

        # fields that will need to be filled in must be set to null
        self.assertNullFinances(mt["you"])
        self.assertNotIn("partner", mt)

        self.assertEqual([], mt["property_set"])

    def test_about_you_have_partner(self):
        update_session("AboutYouForm", have_partner=YES, in_dispute=NO)
        session.checker["category"] = "debt"
        mt = MeansTest()
        mt.update_from_form("AboutYouForm", about_you_post_data(have_partner=YES, in_dispute=NO))

        self.assertEqual(YES, mt["has_partner"])

        self.assertEqual(NO, mt["partner"]["income"]["self_employed"])

        update_session("AboutYouForm", have_partner=YES, in_dispute=NO, partner_is_self_employed=YES)

        session.checker["category"] = "debt"
        mt = MeansTest()

        mt.update_from_form(
            "AboutYouForm", about_you_post_data(have_partner=YES, in_dispute=NO, partner_is_self_employed=YES)
        )

        self.assertEqual(YES, mt["partner"]["income"]["self_employed"])

        update_session("AboutYouForm", have_partner=YES, in_dispute=YES, partner_is_self_employed=YES)

        session.checker["category"] = "debt"
        mt = MeansTest()

        mt.update_from_form(
            "AboutYouForm", about_you_post_data(have_partner=YES, in_dispute=YES, partner_is_self_employed=YES)
        )

        self.assertNotIn("partner", mt)

        self.assertEqual([], mt["property_set"])

    def test_benefits_passported(self):
        session.checker["category"] = "debt"
        mt = MeansTest()
        mt.update_from_form("AboutYouForm", about_you_post_data(on_benefits=YES))
        mt.update_from_form("YourBenefitsForm", {"benefits": ["income_support"]})

        self.assertTrue(mt["on_passported_benefits"])
        expected = {
            "income_support": True,
            "job_seekers_allowance": False,
            "pension_credit": False,
            "universal_credit": False,
            "employment_support": False,
        }
        self.assertEqual(expected, mt["specific_benefits"])

        self.assertIncome(mt["you"]["income"], default=MoneyInterval(0))
        self.assertOutgoings(mt["you"]["deductions"], default=MoneyInterval(0))
        self.assertSavings(mt["you"]["savings"], default=0)

        self.assertEqual([], mt["property_set"])

    def test_benefits_not_passported(self):
        update_session("AboutYouForm", is_employed=YES, have_children=YES)
        session.checker["category"] = "debt"
        mt = MeansTest()
        mt.update_from_form("AboutYouForm", about_you_post_data(on_benefits=YES))
        mt.update_from_form("YourBenefitsForm", {"benefits": "other-benefit"})

        self.assertFalse(mt["on_passported_benefits"])
        expected = {
            "income_support": False,
            "job_seekers_allowance": False,
            "pension_credit": False,
            "universal_credit": False,
            "employment_support": False,
        }
        self.assertEqual(expected, mt["specific_benefits"])
        self.assertNullFinances(mt["you"], income_overrides={"child_benefits": MoneyInterval()})
        self.assertEqual([], mt["property_set"])

    def test_child_benefits(self):
        session.checker["category"] = "debt"
        mt = MeansTest()
        mt.update_from_form("AboutYouForm", about_you_post_data())
        post_data = dict(
            flatten({"child_benefit": post_money_interval("12", "per_week"), "benefits": ["child_benefit"]})
        )
        mt.update_from_form("YourBenefitsForm", post_data)

        self.assertFalse(mt["on_passported_benefits"])
        self.assertEqual(MoneyInterval(1200, "per_week"), mt["you"]["income"]["child_benefits"])

    def test_property(self):
        update_session("AboutYouForm", is_employed=YES, have_children=YES)
        session.checker["category"] = "debt"
        mt = MeansTest()
        mt.update_from_form("AboutYouForm", dict(own_property=YES))
        mt.update_from_form("PropertiesForm", properties_post_data(first_property))

        self.assertIncome(
            mt["you"]["income"],
            default=MoneyInterval(0),
            earnings=MoneyInterval(),
            pension=MoneyInterval(),
            maintenance_received=MoneyInterval(),
            self_employed=None,
        )
        self.assertOutgoings(
            mt["you"]["deductions"],
            default=MoneyInterval(),
            criminal_legalaid_contributions=None,
            mortgage=MoneyInterval("800.00", "per_month"),
        )
        self.assertSavings(mt["you"]["savings"], default=0)

        expected = [
            {
                "value": 1000000,
                "mortgage_left": 900000,
                "share": 100,
                "disputed": NO,
                "rent": MoneyInterval(0),
                "main": YES,
            }
        ]
        self.assertDictEqual(expected[0], mt["property_set"][0])

    def test_multiple_property(self):
        update_session("AboutYouForm", is_employed=YES, have_children=YES)
        session.checker["category"] = "debt"
        mt = MeansTest()
        mt.update_from_form("AboutYouForm", dict(own_property=YES))
        mt.update_from_form("PropertiesForm", properties_post_data(first_property, second_property))

        self.assertIncome(
            mt["you"]["income"],
            default=MoneyInterval(0),
            earnings=MoneyInterval(),
            pension=MoneyInterval(),
            maintenance_received=MoneyInterval(),
            self_employed=None,
        )
        self.assertOutgoings(
            mt["you"]["deductions"],
            default=MoneyInterval(),
            criminal_legalaid_contributions=None,
            mortgage=MoneyInterval("1500.00", "per_month"),
        )
        self.assertSavings(mt["you"]["savings"], default=0)

        expected = [
            {
                "value": 1000000,
                "mortgage_left": 900000,
                "share": 100,
                "disputed": NO,
                "rent": MoneyInterval(0),
                "main": YES,
            },
            {
                "value": 2000000,
                "mortgage_left": 1000000,
                "share": 100,
                "disputed": NO,
                "rent": MoneyInterval(0),
                "main": YES,
            },
        ]
        self.assertDictEqual(expected[0], mt["property_set"][0])
        self.assertDictEqual(expected[1], mt["property_set"][1])

    def test_rent(self):
        session.checker["category"] = "debt"
        mt = MeansTest()

        mt.update_from_form("AboutYouForm", dict(own_property=YES))
        session.checker["AboutYouForm"] = {"have_partner": NO, "own_property": YES}

        prop = rented(first_property, post_money_interval("100.00"))
        mt.update_from_form("PropertiesForm", properties_post_data(prop))
        session.checker["PropertiesForm"] = {"properties": [prop]}

        self.assertIncome(
            mt["you"]["income"],
            default=MoneyInterval(0),
            earnings=MoneyInterval(0),
            pension=MoneyInterval(),
            maintenance_received=MoneyInterval(),
            other_income=MoneyInterval("100.00"),
            self_employed=None,
        )

    def test_multiple_rents(self):
        update_session("AboutYouForm", is_employed=YES, have_children=YES)
        session.checker["category"] = "debt"
        mt = MeansTest()
        mt.update_from_form("AboutYouForm", dict(own_property=YES))
        session.checker["AboutYouForm"] = {"own_property": YES}

        prop1 = rented(first_property, post_money_interval("100.00"))
        prop2 = rented(second_property, post_money_interval("50.00"))
        mt.update_from_form("PropertiesForm", properties_post_data(prop1, prop2))
        session.checker["PropertiesForm"] = {"properties": [prop1, prop2]}

        self.assertIncome(
            mt["you"]["income"],
            default=MoneyInterval(0),
            earnings=MoneyInterval(),
            pension=MoneyInterval(),
            maintenance_received=MoneyInterval(),
            other_income=MoneyInterval("150.00"),
            self_employed=None,
        )

    def test_savings(self):
        session.checker["category"] = "debt"
        mt = MeansTest()
        about_data = {"have_savings": YES, "have_valuables": YES}
        mt.update_from_form("AboutYouForm", about_data)
        session.checker["AboutYouForm"] = about_data

        mt.update_from_form("SavingsForm", {"savings": "1,000.00", "investments": "0.00", "valuables": "500.00"})

        self.assertEqual(100000, mt["you"]["savings"]["bank_balance"])
        self.assertEqual(0, mt["you"]["savings"]["investment_balance"])
        self.assertEqual(50000, mt["you"]["savings"]["asset_balance"])

    def test_additional_benefits(self):
        session.checker["category"] = "debt"
        mt = MeansTest()
        mt.update_from_form("AboutYouForm", about_you_post_data())
        post_data = dict(
            flatten(
                {"benefits": [], "other_benefits": YES, "total_other_benefit": post_money_interval("3", "per_week")}
            )
        )
        mt.update_from_form("AdditionalBenefitsForm", post_data)

        self.assertFalse(mt["on_nass_benefits"])
        self.assertEqual(MoneyInterval(300, "per_week"), mt["you"]["income"]["benefits"])

    def test_nass_benefits(self):
        # NB: asylum support is no longer available in the benefits list

        mt = MeansTest()
        mt.update_from_form(
            "AdditionalBenefitsForm",
            dict(
                flatten(
                    {
                        "benefits": ["asylum-support"],
                        "other_benefits": NO,
                        "total_other_benefit": post_money_interval("0"),
                    }
                )
            ),
        )

        self.assertTrue(mt["on_nass_benefits"])

    def test_child_tax_credits_and_working_tax_credits(self):
        update_session("AboutYouForm", is_employed=YES, have_children=YES)

        mt = MeansTest()
        mt.update_from_form(
            "IncomeForm",
            dict(
                flatten(
                    {
                        "your_income": {
                            "earnings": post_money_interval("0"),
                            "income_tax": post_money_interval("0"),
                            "national_insurance": post_money_interval("0"),
                            "child_tax_credit": post_money_interval("10.00", "per_week"),
                            "working_tax_credit": post_money_interval("10.00"),
                            "maintenance": post_money_interval("0"),
                            "pension": post_money_interval("0"),
                            "other_income": post_money_interval("0"),
                        }
                    }
                )
            ),
        )

        self.assertEqual(MoneyInterval(5333), mt["you"]["income"]["tax_credits"])

    def test_income_self_employed(self):
        session.checker["AboutYouForm"] = {"is_self_employed": YES, "is_employed": NO}

        mt = MeansTest()
        mt.update_from_form("AboutYouForm", about_you_post_data(is_self_employed=YES, is_employed=NO))
        mt.update_from_form(
            "IncomeForm",
            dict(
                flatten(
                    {
                        "your_income": {
                            "earnings": post_money_interval("1"),
                            "income_tax": post_money_interval("2"),
                            "national_insurance": post_money_interval("3"),
                            "working_tax_credit": post_money_interval("4"),
                            "maintenance": post_money_interval("5"),
                            "pension": post_money_interval("6"),
                            "other_income": post_money_interval("7"),
                        }
                    }
                )
            ),
        )

        self.assertEqual(MoneyInterval(0), mt["you"]["income"]["earnings"])
        self.assertEqual(MoneyInterval(100), mt["you"]["income"]["self_employment_drawings"])
        self.assertEqual(MoneyInterval(200), mt["you"]["deductions"]["income_tax"])
        self.assertEqual(MoneyInterval(300), mt["you"]["deductions"]["national_insurance"])
        self.assertEqual(MoneyInterval(400), mt["you"]["income"]["tax_credits"])
        self.assertEqual(MoneyInterval(500), mt["you"]["income"]["maintenance_received"])
        self.assertEqual(MoneyInterval(600), mt["you"]["income"]["pension"])
        self.assertEqual(MoneyInterval(700), mt["you"]["income"]["other_income"])

    def test_partner_income(self):
        session.checker["AboutYouForm"] = {"have_partner": YES, "partner_is_employed": YES}

        mt = MeansTest()
        mt.update_from_form(
            "IncomeForm",
            dict(
                flatten(
                    {
                        "your_income": {
                            "earnings": post_money_interval("0"),
                            "income_tax": post_money_interval("0"),
                            "national_insurance": post_money_interval("0"),
                            "working_tax_credit": post_money_interval("0"),
                            "maintenance": post_money_interval("0"),
                            "pension": post_money_interval("0"),
                            "other_income": post_money_interval("0"),
                        },
                        "partner_income": {
                            "earnings": post_money_interval("1"),
                            "income_tax": post_money_interval("2"),
                            "national_insurance": post_money_interval("3"),
                            "working_tax_credit": post_money_interval("4"),
                            "maintenance": post_money_interval("5"),
                            "pension": post_money_interval("6"),
                            "other_income": post_money_interval("7"),
                        },
                    }
                )
            ),
        )

        self.assertEqual(MoneyInterval(100), mt["partner"]["income"]["earnings"])
        self.assertEqual(MoneyInterval(200), mt["partner"]["deductions"]["income_tax"])
        self.assertEqual(MoneyInterval(300), mt["partner"]["deductions"]["national_insurance"])
        self.assertEqual(MoneyInterval(400), mt["partner"]["income"]["tax_credits"])
        self.assertEqual(MoneyInterval(500), mt["partner"]["income"]["maintenance_received"])
        self.assertEqual(MoneyInterval(600), mt["partner"]["income"]["pension"])
        self.assertEqual(MoneyInterval(700), mt["partner"]["income"]["other_income"])
