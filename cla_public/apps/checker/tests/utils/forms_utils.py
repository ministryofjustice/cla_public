from decimal import InvalidOperation
from flask import session

from cla_public.apps.checker.constants import YES, NO
from cla_public.libs.money_interval import MoneyInterval


CATEGORY_MAPPING = {
    'Welfare': 'benefits',
    'Debt': 'debt',
}

BENEFITS_MAPPING = {
    'Income Support': 'income_support',
    'Job Seekers Allowance': 'job_seekers_allowance',
    'Employment and Support Allowance': 'employment_support'
}

NON_FORM_FIELDS = ['csrf_token', 'comment']


def flatten_dict(field_name, data_dict):
        return {'%s-%s' % (field_name, key): val for key, val in
                data_dict.items()}


def flatten_list_of_dicts(field_name, data_list):
    return {'%s-%s-%s' % (field_name, num, key): val for num, d in
            enumerate(data_list) for key, val in d.items()}


class ProblemFormMixin(object):
    """ProblemForm"""

    def problemform_categories(self):
        return CATEGORY_MAPPING[self._law_area]


class AboutYouFormMixin(object):
    """AboutYouForm"""

    def aboutyouform_have_valuables(self):
        return YES if self.n_greater_than(
            self.savingsform_valuables(), x=500) else NO

    def aboutyouform_have_children(self):
        return self.yes_or_no(
            self._children,
            self._under16 and int(self._under16) > 0)

    def aboutyouform_num_children(self):
        return self.number_if_yes(
            self._under16,
            self.aboutyouform_have_children())

    def aboutyouform_is_employed(self):
        return self.n_to_yes_no(self._earnings_1)

    def aboutyouform_have_partner(self):
        return self.yes_or_no(self._partner)

    def aboutyouform_have_dependants(self):
        return self.yes_or_no(
            self._children,
            self._over16 and int(self._over16) > 0)

    def aboutyouform_num_dependants(self):
        return self.number_if_yes(
            self._over16,
            self.aboutyouform_have_dependants())

    def aboutyouform_in_dispute(self):
        return NO

    def aboutyouform_have_savings(self):
        return YES if self.n_greater_than(self.savingsform_savings()) or \
                      self.n_greater_than(self.savingsform_investments()) \
                      else NO

    def aboutyouform_partner_is_self_employed(self):
        return self.yes_or_no(self._pselfemp)

    def aboutyouform_partner_is_employed(self):
        return self.n_to_yes_no(self._partner_earnings)

    def aboutyouform_aged_60_or_over(self):
        return self.yes_or_no(self._60_or_over)

    def aboutyouform_is_self_employed(self):
        return self.yes_or_no(self._selfemp)

    def aboutyouform_on_benefits(self):
        return self.yes_or_no(
            self._benefits,
            bool(self.yourbenefitsform_benefits()))

    def aboutyouform_own_property(self):
        return self.yes_or_no(self._own_property)


class BenefitsFormMixin(object):
    """BenefitsForm"""

    def yourbenefitsform_benefits(self):
        return [BENEFITS_MAPPING[x.strip()] for x in self._benefit.split(';')
                if x.strip() in BENEFITS_MAPPING]


class PropertiesFormMixin(object):
    """PropertiesForm"""

    def propertyform_mortgage_payments(self, n):
        if n > 1:
            return 0
        val = 0
        if self._mortgage_deduction:
            val += self._mortgage_deduction
        if session.has_partner and self._pmortgage:
            val += self._pmortgage
        return val

    def propertyform_other_shareholders(self, n):
        return NO if getattr(self, '_prop%s_share' % n) == 100 else YES

    def propertyform_in_dispute(self, n):
        return self.yes_or_no(getattr(self, '_prop%s_disputed' % n))

    def propertiesform_properties(self):
        properties = []
        number_properties = sum([1 for n in range(1, 3) if
                                 unicode(getattr(self, '_prop%s_value' % n))])
        for n in range(1, number_properties + 1):
            property = {
                'is_main_home': YES if n == 1 else NO,
                'other_shareholders': self.propertyform_other_shareholders(n),
                'property_value': getattr(self, '_prop%s_value' % n),
                'mortgage_remaining': getattr(self, '_prop%s_mortgage' % n),
                'mortgage_payments': self.propertyform_mortgage_payments(n),
                'is_rented': NO,
                'in_dispute': self.propertyform_in_dispute(n),
            }

            property.update(flatten_dict('rent_amount', MoneyInterval(0)))

            properties.append(property)

        return properties

    def propertiesform_data(self):
        return flatten_list_of_dicts(
            'properties', self.propertiesform_properties())


class SavingsFormMixin(object):
    """SavingsForm"""

    def savingsform_savings(self):
        s = self.get_total_if_partner(self._savings, self._psavings)
        if self.savingsform_valuables() and not \
                self.n_greater_than(self.savingsform_valuables(), x=500):
            s += self.savingsform_valuables()
        s += self.get_total_if_partner(self._owed, self._powed)
        return s

    def savingsform_investments(self):
        return self.get_total_if_partner(self._investments, self._pinvestments)

    def savingsform_valuables(self):
        return self.get_total_if_partner(self._valuable, self._pvaluable)


class TaxCreditsFormMixin(object):
    """TaxCreditsForm"""

    def taxcreditsform_child_benefit(self):
        return MoneyInterval(0, 'per_week')

    def taxcreditsform_child_tax_credit(self):
        return MoneyInterval(0, 'per_week')

    def taxcreditsform_benefits(self):
        return []

    def taxcreditsform_other_benefits(self):
        return NO

    def taxcreditsform_total_other_benefit(self):
        return MoneyInterval(0, 'per_week')

    def taxcreditsform_data(self):
        d = {
            'benefits': self.taxcreditsform_benefits(),
            'other_benefits': self.taxcreditsform_other_benefits()
        }

        d.update(flatten_dict(
            'child_benefit', self.taxcreditsform_child_benefit()))
        d.update(flatten_dict(
            'child_tax_credit', self.taxcreditsform_child_tax_credit()))
        d.update(flatten_dict(
            'total_other_benefit', self.taxcreditsform_total_other_benefit()))

        return d


class IncomeFormMixin(object):
    """IncomeFormMixin"""

    def incomeform_your_income(self):
        return {
            'earnings': MoneyInterval(self._earnings_1 or 0),
            'income_tax': MoneyInterval(self._tax or 0),
            'national_insurance': MoneyInterval(self._ni or 0),
            'working_tax_credit': MoneyInterval(0),
            'maintenance': MoneyInterval(0),
            'pension': MoneyInterval(0),
            'other_income': MoneyInterval(self._other_income or 0),
        }

    def incomeform_partner_income(self):
        return {
            'earnings': MoneyInterval(self._partner_earnings or 0),
            'income_tax': MoneyInterval(self._ptax or 0),
            'national_insurance': MoneyInterval(self._pni or 0),
            'working_tax_credit': MoneyInterval(0),
            'maintenance': MoneyInterval(0),
            'pension': MoneyInterval(0),
            'other_income': MoneyInterval(self._partner_other_income or 0),
        }

    def incomeform_data(self):
        d = flatten_dict('your_income', self.incomeform_your_income())

        if session.has_partner:
            d.update(flatten_dict(
                'partner_income', self.incomeform_partner_income()))

        data = {}
        for key, value in d.iteritems():
            data.update(flatten_dict(key, value))

        return data


class OutgoingsFormMixin(object):
    """OutgoingsForm"""

    def outgoingsform_rent(self):
        return MoneyInterval(
            self.get_total_if_partner(self._rent, self._prent))

    def outgoingsform_maintenance(self):
        return MoneyInterval(
            self.get_total_if_partner(self._maint, self._pmaint))

    def outgoingsform_income_contribution(self):
        return self.get_total_if_partner(
            self._contribution, self._pcontribution)

    def outgoingsform_childcare(self):
        return MoneyInterval(
            self.get_total_if_partner(self._childcare, self._pchildcare))

    def outgoingsform_data(self):
        d = {
            'income_contribution': self.outgoingsform_income_contribution()
        }

        d.update(flatten_dict('rent', self.outgoingsform_rent()))
        d.update(flatten_dict('maintenance', self.outgoingsform_maintenance()))
        d.update(flatten_dict('childcare', self.outgoingsform_childcare()))

        return d


class FormDataConverter(
        ProblemFormMixin,
        AboutYouFormMixin,
        BenefitsFormMixin,
        PropertiesFormMixin,
        SavingsFormMixin,
        TaxCreditsFormMixin,
        IncomeFormMixin,
        OutgoingsFormMixin):
    """Process data row from means test row and return values for each form"""
    def __init__(self, **values):
        self.__dict__.update(values)

    def get_value(self, form_class, field):
        return getattr(self, '%s_%s' % (form_class.__name__.lower(), field))()

    def get_form_data(self, form_class):
        method_name = '%s_data' % form_class.__name__.lower()
        if hasattr(self, method_name):
            return getattr(self, method_name)()
        ret = {}
        needed = lambda field: field not in NON_FORM_FIELDS
        fields = filter(needed, form_class()._fields.keys())
        for field in fields:
            ret[field] = self.get_value(form_class, field)
        return ret

    def yes_or_no(self, spreadsheet_value, extra_cond=True):
        return YES if spreadsheet_value == 'Y' and extra_cond else NO

    def n_to_yes_no(self, n):
        return YES if self.n_greater_than(n) else NO

    def n_greater_than(self, n, x=0):
        try:
            return True if n > x else False
        except InvalidOperation:
            return False

    def number_if_yes(self, n, d):
        return int(n) if n and int(n) > 0 and d == YES else None

    def get_total_if_partner(self, your_value, partner_value):
        val = 0
        if your_value:
            val += your_value
        if session.has_partner and partner_value:
            val += partner_value
        return val
