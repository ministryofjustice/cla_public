from __future__ import unicode_literals
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
    # ProblemForm

    def problemform_categories(self):
        return CATEGORY_MAPPING[self._law_area]


class AboutYouFormMixin(object):
        # AboutYouForm

    def aboutyouform_have_valuables(self):
        return self.n_to_yes_no(self._valuable)

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
        return YES if self.n_greater_than_zero(self._savings) or \
                      self.n_greater_than_zero(self._investments) else NO

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
    # BenefitsForm

    def yourbenefitsform_benefits(self):
        return [BENEFITS_MAPPING[x.strip()] for x in self._benefit.split(';')
                if x.strip() in BENEFITS_MAPPING]


class PropertiesFormMixin(object):
    # PropertyForm

    def propertyform_is_main_home(self):
        return

    def propertyform_other_shareholders(self):
        return

    def propertyform_property_value(self):
        return

    def propertyform_mortgage_remaining(self):
        return

    def propertyform_mortgage_payments(self):
        return

    def propertyform_is_rented(self):
        return

    def propertyform_in_dispute(self):
        return

    # PropertiesForm

    def propertiesform_properties(self):
        mt_fields = ['value', 'mortgage', 'joint', 'disputed', 'share']
        properties = []
        for n in range(1, 3):
            value = getattr(self, '_prop%s_value' % n)
            if self.n_greater_than_zero(value):
                rent_amount = {
                    'per_interval_value': '30',
                    'interval_period': 'per_week'
                }

                property = {
                    'is_main_home': YES,
                    'other_shareholders': NO,
                    'property_value': '100',
                    'mortgage_remaining': '99',
                    'mortgage_payments': '1',
                    'is_rented': YES,
                    'in_dispute': NO
                }

                property.update(flatten_dict('rent_amount', rent_amount))

                properties.append(property)

        return flatten_list_of_dicts('properties', properties)


