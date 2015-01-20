from __future__ import unicode_literals
from flask import session

from cla_public.apps.checker.api import money_interval
from cla_public.apps.checker.constants import YES, NO


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
        return {'%s-%s' % (field_name, key): val for key, val in data_dict.items()}


def flatten_list_of_dicts(field_name, data_list):
    return {'%s-%s-%s' % (field_name, num, key): val for num, d in enumerate(data_list) for key, val in d.items()}


class ProblemFormMixin(object):
    """ProblemForm"""

    def problemform_categories(self):
        return CATEGORY_MAPPING[self._law_area]


class AboutYouFormMixin(object):
    """AboutYouForm"""

    def aboutyouform_have_valuables(self):
        return YES if self.n_greater_than(self.savingsform_valuables(), x=500) else NO

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
        return self.n_to_yes_no(self._partner)

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
                      self.n_greater_than(self.savingsform_investments()) else NO

    def aboutyouform_partner_is_self_employed(self):
        return self.yes_or_no(self._selfemp)

    def aboutyouform_partner_is_employed(self):
        return self.n_to_yes_no(self._partner_earnings)

    def aboutyouform_aged_60_or_over(self):
        return self.n_to_yes_no(self._60_or_over)

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

    def propertyform_mortgage_payments(self):
        val = 0.00
        if self._mortgage_deduction:
            val += float(self._mortgage_deduction)
        if session.has_partner and self._pmortgage:
            val += float(self._pmortgage)
        return val

    def propertiesform_properties(self):
        properties = []
        number_properties = sum([1 for n in range(1, 3) if unicode(getattr(self, '_prop%s_value' % n))])
        for n in range(1, number_properties + 1):
            value = getattr(self, '_prop%s_value' % n)
            property = {
                'is_main_home': YES if n == 1 else NO,
                'other_shareholders': NO if getattr(self, '_prop%s_share' % n) == 100 else YES,
                'property_value': value,
                'mortgage_remaining': getattr(self, '_prop%s_mortgage' % n),
                'mortgage_payments': self.propertyform_mortgage_payments() if n == 1 else 0,
                'is_rented': NO,
                'in_dispute': self.yes_or_no(getattr(self, '_prop%s_disputed' % n)),
            }

            properties.append(property)

        return properties

    def propertiesform_data(self):
        def flattern_rent(p):
            if 'rent_amount' in p:
                p.update(flatten_dict('rent_amount', p['rent_amount']))
                del p['rent_amount']
            return p

        properties = map(flattern_rent, self.propertiesform_properties())
        return flatten_list_of_dicts('properties', properties)


class SavingsFormMixin(object):
    """SavingsForm"""

    def savingsform_savings(self):
        s = float(self._savings or 0)
        if self.savingsform_valuables() and not \
                self.n_greater_than(self.savingsform_valuables(), x=500):
            s += float(self.savingsform_valuables())
        if self._owed:
            s += float(self._owed)
        if session.has_partner:
            if self._powed:
                s += float(self._powed)
        return s

    def savingsform_investments(self):
        return self.get_total_if_partner(self._investments, self._pinvestments)

    def savingsform_valuables(self):
        return self.get_total_if_partner(self._valuable, self._pvaluable)


class TaxCreditsFormMixin(object):
    """TaxCreditsForm"""

    def taxcreditsform_child_benefit(self):
        return money_interval(0)

    def taxcreditsform_child_tax_credit(self):
        return money_interval(0)

    def taxcreditsform_benefits(self):
        return []

    def taxcreditsform_other_benefits(self):
        return NO

    def taxcreditsform_total_other_benefit(self):
        return money_interval(0)

    def taxcreditsform_data(self):
        d = {
            'benefits': self.taxcreditsform_benefits(),
            'other_benefits': self.taxcreditsform_other_benefits()
        }

        d.update(flatten_dict('child_benefit', self.taxcreditsform_child_benefit()))
        d.update(flatten_dict('child_tax_credit', self.taxcreditsform_child_tax_credit()))
        d.update(flatten_dict('total_other_benefit', self.taxcreditsform_total_other_benefit()))

        return d


class IncomeFormMixin(object):
    """IncomeFormMixin"""

    def incomeform_your_income(self):
        return {
            'earnings': money_interval(self._earnings_1 or 0),
            'income_tax': money_interval(self._tax or 0),
            'national_insurance': money_interval(self._ni or 0),
            'working_tax_credit': money_interval(0),
            'maintenance': money_interval(self._maint or 0),
            'pension': money_interval(0),
            'other_income': money_interval(self._other_income or 0),
        }

    def incomeform_partner_income(self):
        return {
            'earnings': money_interval(self._partner_earnings or 0),
            'income_tax': money_interval(self._ptax or 0),
            'national_insurance': money_interval(self._pni or 0),
            'working_tax_credit': money_interval(0),
            'maintenance': money_interval(self._pmaint or 0),
            'pension': money_interval(0),
            'other_income': money_interval(self._partner_other_income or 0),
        }

    def incomeform_data(self):
        d = flatten_dict('your_income', self.incomeform_your_income())

        if session.has_partner:
            d.update(flatten_dict('partner_income', self.incomeform_partner_income()))

        data = {}
        for key, value in d.iteritems():
            data.update(flatten_dict(key, value))

        return data


class OutgoingsFormMixin(object):
    """OutgoingsForm"""

    def outgoingsform_rent(self):
        return money_interval(
            self.get_total_if_partner(self._rent, self._prent))

    def outgoingsform_maintenance(self):
        return money_interval(
            self.get_total_if_partner(self._maint, self._pmaint))

    def outgoingsform_income_contribution(self):
        return self.get_total_if_partner(self._contribution, self._pcontribution)

    def outgoingsform_childcare(self):
        return money_interval(
            self.get_total_if_partner(self._childcare, self._pchildcare))

    def outgoingsform_data(self):
        d = {
            'income_contribution': self.outgoingsform_income_contribution()
        }

        d.update(flatten_dict('rent', self.outgoingsform_rent()))
        d.update(flatten_dict('maintenance', self.outgoingsform_maintenance()))
        d.update(flatten_dict('childcare', self.outgoingsform_childcare()))

        return d
