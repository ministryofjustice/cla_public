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
    # PropertiesForm

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
                'mortgage_payments': self._mortgage_deduction if n == 1 and self._mortgage_deduction else 0,
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


