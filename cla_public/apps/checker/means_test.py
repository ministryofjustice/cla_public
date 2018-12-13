# coding: utf-8
"Means Test class"

from collections import Mapping
from copy import deepcopy
import logging
import sys

from flask import current_app, session
from slumber.exceptions import SlumberBaseException
from requests.exceptions import ConnectionError, Timeout

from cla_public.apps.checker.api import get_api_connection
from cla_public.apps.checker.constants import YES, NO, PASSPORTED_BENEFITS, CATEGORY_ID_MAPPING
from cla_public.apps.checker.utils import nass, passported
from cla_public.libs.money_interval import MoneyInterval, to_amount
from cla_public.libs.utils import classproperty, flatten


log = logging.getLogger(__name__)


def mi(field, val):
    amount = "%s-per_interval_value" % field
    period = "%s-interval_period" % field
    return {"per_interval_value": val(amount), "interval_period": val(period)}


def recursive_update(orig, other):
    for key, val in other.iteritems():

        if key not in orig:
            if isinstance(val, Mapping):
                orig[key] = deepcopy(val)
            else:
                orig[key] = val

        elif orig[key] == val:
            continue

        elif key == "notes" and orig[key] != val:
            orig[key] = "{0}\n\n{1}".format(orig[key], val)

        elif isinstance(val, Mapping):
            if MoneyInterval.is_money_interval(val):
                orig[key] = MoneyInterval(val)
            elif val != {}:
                if not isinstance(orig[key], Mapping):
                    orig[key] = {}
                orig[key] = recursive_update(orig[key], val)

        elif isinstance(val, list):
            orig[key] = val

        else:
            orig[key] = val

    return orig


class AboutYouPayload(dict):
    def __init__(self, form_data={}):
        super(AboutYouPayload, self).__init__()

        yes = lambda field: form_data.get(field) == YES  # noqa: E731
        val = lambda field: form_data.get(field)  # noqa: E731

        payload = {
            "dependants_young": val("num_children") if yes("have_children") else 0,
            "dependants_old": val("num_dependants") if yes("have_dependants") else 0,
            "is_you_or_your_partner_over_60": val("aged_60_or_over"),
            "has_partner": YES if yes("have_partner") and not yes("in_dispute") else NO,
            "you": {"income": {"self_employed": val("is_self_employed")}},
        }

        if yes("have_partner") and not yes("in_dispute") and yes("partner_is_self_employed"):
            payload["partner"] = {"income": {"self_employed": val("partner_is_self_employed")}}

        if yes("own_property"):
            payload = recursive_update(payload, PropertiesPayload())
        else:
            payload = recursive_update(payload, PropertiesPayload.default)

        if yes("have_savings") or yes("have_valuables"):
            payload = recursive_update(payload, SavingsPayload())
        else:
            payload = recursive_update(payload, SavingsPayload.default)

        if not yes("on_benefits"):
            payload = recursive_update(payload, YourBenefitsPayload.default)

        payload = recursive_update(payload, IncomePayload())
        payload = recursive_update(payload, OutgoingsPayload())

        self.update(payload)


class YourBenefitsPayload(dict):
    @classproperty
    def default(cls):
        return {"specific_benefits": {}, "on_passported_benefits": NO}

    def __init__(self, form_data={}):
        super(YourBenefitsPayload, self).__init__()

        is_selected = lambda ben: ben in form_data["benefits"]  # noqa: E731
        benefits = {ben: is_selected(ben) for ben in PASSPORTED_BENEFITS}  # noqa: E731
        is_passported = passported(form_data["benefits"])  # noqa: E731

        payload = {"specific_benefits": benefits, "on_passported_benefits": is_passported}

        if is_passported:
            payload = recursive_update(payload, IncomePayload.default)
            payload = recursive_update(payload, OutgoingsPayload.default)
        else:
            val = lambda field: form_data.get(field)  # noqa: E731

            payload["you"] = {"income": {"child_benefits": MoneyInterval(mi("child_benefit", val))}}

        self.update(payload)


class AdditionalBenefitsPayload(dict):
    def __init__(self, form_data={}):
        super(AdditionalBenefitsPayload, self).__init__()

        val = lambda field: form_data.get(field)  # noqa: E731
        yes = lambda field: form_data[field] == YES  # noqa: E731

        benefits = val("benefits")

        payload = {
            "on_nass_benefits": nass(benefits),  # always False
            "you": {
                "income": {
                    "benefits": MoneyInterval(mi("total_other_benefit", val))
                    if yes("other_benefits")
                    else MoneyInterval(0)
                }
            },
        }

        if benefits:
            payload["notes"] = u"Other benefits:\n - {0}".format("\n - ".join(benefits))

        self.update(payload)


class PropertyPayload(dict):
    def __init__(self, form_data={}):
        super(PropertyPayload, self).__init__()

        val = lambda field: form_data.get(field)  # noqa: E731
        yes = lambda field: form_data.get(field) == YES  # noqa: E731
        no = lambda field: form_data.get(field) == NO  # noqa: E731

        self.update(
            {
                "value": to_amount(val("property_value")),
                "mortgage_left": to_amount(val("mortgage_remaining")),
                "share": 100 if no("other_shareholders") else None,
                "disputed": val("in_dispute"),
                "rent": MoneyInterval(mi("rent_amount", val)) if yes("is_rented") else MoneyInterval(0),
                "main": val("is_main_home"),
            }
        )


class PropertiesPayload(dict):
    @classproperty
    def default(cls):
        return {
            "property_set": [],
            "you": {"deductions": {"mortgage": MoneyInterval(0)}, "income": {"other_income": MoneyInterval(0)}},
        }

    def __init__(self, form_data={}):
        super(PropertiesPayload, self).__init__()

        def prop(index):
            if "properties-%d-is_main_home" % index not in form_data:
                return None
            prop_data = dict(
                [(key[13:], val) for key, val in form_data.items() if key.startswith("properties-%d-" % index)]
            )
            return PropertyPayload(prop_data)

        properties = filter(None, map(prop, range(3)))
        if not properties and session.checker.owns_property:
            properties.append(PropertyPayload())

        def mortgage(index):
            return MoneyInterval(form_data.get("properties-%d-mortgage_payments" % index, 0))

        total_mortgage = sum(map(mortgage, range(len(properties))))

        total_rent = sum(p["rent"] for p in properties)

        self.update(
            {
                "property_set": properties,
                "you": {"income": {"other_income": total_rent}, "deductions": {"mortgage": total_mortgage}},
            }
        )


class SavingsPayload(dict):
    @classproperty
    def default(cls):
        return {"you": {"savings": {"bank_balance": 0, "investment_balance": 0, "asset_balance": 0}}}

    def __init__(self, form_data={}):
        super(SavingsPayload, self).__init__()

        val = lambda field: form_data.get(field)  # noqa: E731

        savings = 0
        investments = 0
        valuables = 0

        if session.checker.has_savings:
            savings = val("savings")
            investments = val("investments")
        if session.checker.has_valuables:
            valuables = val("valuables")

        self.update(
            {
                "you": {
                    "savings": {
                        "bank_balance": to_amount(savings),
                        "investment_balance": to_amount(investments),
                        "asset_balance": to_amount(valuables),
                    }
                }
            }
        )


class IncomePayload(dict):
    @classproperty
    def default(cls):
        income = lambda: {  # noqa: E731
            "income": {
                "earnings": MoneyInterval(0),
                "tax_credits": MoneyInterval(0),
                "other_income": MoneyInterval(0),
                "self_employment_drawings": MoneyInterval(0),
                "maintenance_received": MoneyInterval(0),
                "pension": MoneyInterval(0),
            },
            "deductions": {"income_tax": MoneyInterval(0), "national_insurance": MoneyInterval(0)},
        }

        return {"you": income(), "partner": income()}

    def __init__(self, form_data={}):
        super(IncomePayload, self).__init__()

        def income(person, prefix_, self_employed=False, employed=False):
            prefix = lambda field: "{0}-{1}".format(prefix_, field)  # noqa: E731
            val = lambda field: form_data.get(prefix(field))  # noqa: E731
            child_tax_credit = MoneyInterval(mi("child_tax_credit", val)) if person == "you" else MoneyInterval(0)
            payload = {
                person: {
                    "income": {
                        "earnings": MoneyInterval(mi("earnings", val)),
                        "self_employment_drawings": MoneyInterval(0),
                        "tax_credits": MoneyInterval(mi("working_tax_credit", val)) + child_tax_credit,
                        "maintenance_received": MoneyInterval(mi("maintenance", val)),
                        "pension": MoneyInterval(mi("pension", val)),
                        "other_income": MoneyInterval(mi("other_income", val)),
                    },
                    "deductions": {
                        "income_tax": MoneyInterval(mi("income_tax", val)),
                        "national_insurance": MoneyInterval(mi("national_insurance", val)),
                    },
                }
            }

            if self_employed:
                payload[person]["income"]["earnings"] = MoneyInterval(0)
                payload[person]["income"]["self_employment_drawings"] = MoneyInterval(mi("earnings", val))

            if not employed:
                payload[person]["income"]["earnings"] = MoneyInterval(0)
                payload[person]["income"]["self_employment_drawings"] = MoneyInterval(0)
                payload[person]["income"]["tax_credits"] = MoneyInterval(0)
                payload[person]["deductions"]["income_tax"] = MoneyInterval(0)
                payload[person]["deductions"]["national_insurance"] = MoneyInterval(0)

            return payload

        payload = income(
            "you",
            "your_income",
            session.checker.is_self_employed and not session.checker.is_employed,
            session.checker.is_self_employed or session.checker.is_employed,
        )

        if session.checker.owns_property:
            rents = [
                MoneyInterval(p["rent_amount"])
                for p in session.checker.get("PropertiesForm", {}).get("properties", [])
            ]
            total_rent = sum(rents)
            payload["you"]["income"]["other_income"] += total_rent

        if session.checker.has_partner:
            partner_payload = income(
                "partner",
                "partner_income",
                session.checker.partner_is_self_employed and not session.checker.partner_is_employed,
                session.checker.partner_is_self_employed or session.checker.partner_is_employed,
            )
            payload = recursive_update(payload, partner_payload)

        self.update(payload)


class OutgoingsPayload(dict):
    @classproperty
    def default(cls):
        return {
            "you": {
                "deductions": {
                    "rent": MoneyInterval(0),
                    "maintenance": MoneyInterval(0),
                    "childcare": MoneyInterval(0),
                    "criminal_legalaid_contributions": 0,
                }
            }
        }

    def __init__(self, form_data={}):
        super(OutgoingsPayload, self).__init__()

        val = lambda field: form_data.get(field)  # noqa: E731
        self.update(
            {
                "you": {
                    "deductions": {
                        "rent": MoneyInterval(mi("rent", val)),
                        "maintenance": MoneyInterval(mi("maintenance", val)),
                        "criminal_legalaid_contributions": to_amount(val("income_contribution")),
                        "childcare": MoneyInterval(mi("childcare", val)),
                    }
                }
            }
        )
        if not session.checker.has_children and not session.checker.has_dependants:
            self["you"]["deductions"]["childcare"] = MoneyInterval(0)


class MeansTestError(Exception):
    pass


class MeansTest(dict):
    """
    Encapsulates the means test data and saving to and querying the API
    """

    def __init__(self, *args, **kwargs):
        super(MeansTest, self).__init__(*args, **kwargs)

        self.reference = session.checker.get("eligibility_check", None)

        def zero_finances():
            return {
                "income": {
                    "earnings": MoneyInterval(0),
                    "benefits": MoneyInterval(0),
                    "tax_credits": MoneyInterval(0),
                    "child_benefits": MoneyInterval(0),
                    "other_income": MoneyInterval(0),
                    "self_employment_drawings": MoneyInterval(0),
                    "maintenance_received": MoneyInterval(0),
                    "pension": MoneyInterval(0),
                    "self_employed": NO,
                },
                "savings": {"credit_balance": 0, "investment_balance": 0, "asset_balance": 0, "bank_balance": 0},
                "deductions": {
                    "income_tax": MoneyInterval(0),
                    "mortgage": MoneyInterval(0),
                    "childcare": MoneyInterval(0),
                    "rent": MoneyInterval(0),
                    "maintenance": MoneyInterval(0),
                    "national_insurance": MoneyInterval(0),
                    "criminal_legalaid_contributions": 0,
                },
            }

        self.update(
            {
                "you": zero_finances(),
                "dependants_young": 0,
                "dependants_old": 0,
                "on_passported_benefits": NO,
                "on_nass_benefits": NO,
                "specific_benefits": {},
            }
        )

        if session.checker.has_partner:
            self.update({"partner": zero_finances()})

        if "category" in session.checker:
            category = session.checker["category"]
            self["category"] = CATEGORY_ID_MAPPING.get(category, category)

    def update(self, other={}, **kwargs):
        """
        Recursively merge dicts into self
        """
        other.update(kwargs)
        recursive_update(self, other)

    def update_from_form(self, form, form_data):
        payload_class = "{0}Payload".format(form.replace("Form", ""))
        payload = getattr(sys.modules[__name__], payload_class)
        self.update(payload(form_data))

    def update_from_session(self):

        forms = [
            "AboutYouForm",
            "YourBenefitsForm",
            "AdditionalBenefitsForm",
            "PropertiesForm",
            "SavingsForm",
            "IncomeForm",
            "OutgoingsForm",
        ]

        for form in forms:
            if form in session.checker:
                self.update_from_form(form, flatten(session.checker[form]))

    def save(self):
        sentry = getattr(current_app, "sentry", None)
        try:
            backend = get_api_connection()

            if self.reference:
                backend.eligibility_check(self.reference).patch(self)
            else:
                response = backend.eligibility_check.post(self)
                self.reference = response["reference"]
                session.checker["eligibility_check"] = self.reference
        except (ConnectionError, Timeout, SlumberBaseException):
            if sentry:
                sentry.captureException()
            else:
                log.exception("Failed saving eligibility check")
            raise MeansTestError()

    def is_eligible(self):
        sentry = getattr(current_app, "sentry", None)
        try:
            backend = get_api_connection()

            if self.reference:
                api = backend.eligibility_check(self.reference).is_eligible()
                response = api.post({})
                return response.get("is_eligible")
        except (ConnectionError, Timeout, SlumberBaseException):
            if sentry:
                sentry.captureException()
            else:
                log.exception("Failed testing eligibility")
            raise MeansTestError()
