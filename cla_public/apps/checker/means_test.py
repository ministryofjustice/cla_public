from collections import Mapping
from copy import deepcopy

from cla_public.apps.checker.api import get_api_connection
from cla_public.apps.checker.constants import YES, NO
from cla_public.libs.money_interval import MoneyInterval


def recursive_update(orig, other):
    for key, val in other.iteritems():

        if key not in orig:
            if isinstance(val, Mapping):
                orig[key] = deepcopy(val)
            else:
                orig[key] = val

        elif orig[key] == val:
            continue

        elif key == 'notes' and orig[key] != val:
            orig[key] = '{0}\n\n{1}'.format(orig[key], val)

        elif isinstance(val, Mapping):
            if MoneyInterval.is_money_interval(val):
                orig[key] = MoneyInterval(val)
            elif val != {}:
                orig[key] = recursive_update(orig[key], val)

        elif isinstance(val, list):
            orig[key] = orig.get(key, []) + val

        else:
            orig[key] = val

    return orig


class MeansTest(dict):
    """
    Encapsulates the means test data and saving to and querying the API
    """

    def __init__(self, *args, **kwargs):
        super(MeansTest, self).__init__(*args, **kwargs)

        self.reference = None

        zero_finances = {
            'income': {
                'earnings': MoneyInterval(0),
                'benefits': MoneyInterval(0),
                'tax_credits': MoneyInterval(0),
                'child_benefits': MoneyInterval(0),
                'other_income': MoneyInterval(0),
                'self_employment_drawings': MoneyInterval(0),
                'maintenance_received': MoneyInterval(0),
                'pension': MoneyInterval(0),
                'total': 0,
                'self_employed': NO
            },
            'savings': {
                'credit_balance': 0,
                'investment_balance': 0,
                'asset_balance': 0,
                'bank_balance': 0,
                'total': 0
            },
            'deductions': {
                'income_tax': MoneyInterval(0),
                'mortgage': MoneyInterval(0),
                'childcare': MoneyInterval(0),
                'rent': MoneyInterval(0),
                'maintenance': MoneyInterval(0),
                'national_insurance': MoneyInterval(0),
                'criminal_legalaid_contributions': 0
            }
        }

        self.update({
            'you': deepcopy(zero_finances),
            'partner': deepcopy(zero_finances),
            'dependants_young': 0,
            'dependants_old': 0,
            'on_passported_benefits': NO,
            'on_nass_benefits': NO,
            'specific_benefits': {}
        })

    def update(self, other={}, **kwargs):
        """
        Recursively merge dicts into self
        """
        other.update(kwargs)
        recursive_update(self, other)

    def save(self):
        backend = get_api_connection()

        if self.reference:
            backend.eligibility_check(self.reference).patch(self)
        else:
            response = backend.eligibility_check.post(self)
            self.reference = response['reference']

    def is_eligible(self):
        backend = get_api_connection()

        if self.reference:
            api = backend.eligibility_check(self.reference).is_eligible()
            response = api.post({})
            return response.get('is_eligible')
