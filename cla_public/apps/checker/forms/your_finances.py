# -*- coding: utf-8 -*-
import re
import itertools

from django import forms
from django.utils.translation import ugettext as _
from django.forms.formsets import formset_factory, BaseFormSet, \
    TOTAL_FORM_COUNT, INITIAL_FORM_COUNT

import form_utils.forms

from cla_common.forms import MultipleFormsForm
from cla_common.money_interval.forms import MoneyIntervalField

from ..fields import RadioBooleanField, MoneyField

from .base import CheckerWizardMixin, EligibilityMixin


OWNED_BY_CHOICES = [
    (1, 'Owned by me'),
    (0, 'Joint names')
]


class YourFinancesFormMixin(EligibilityMixin, CheckerWizardMixin):
    form_tag = 'your_finances'

    def _prepare_for_init(self, kwargs):
        super(YourFinancesFormMixin, self)._prepare_for_init(kwargs)

        # pop these from kwargs
        self.has_partner = kwargs.pop('has_partner', True)
        self.has_property = kwargs.pop('has_property', True)
        self.has_children = kwargs.pop('has_children', True)
        self.has_benefits = kwargs.pop('has_benefits', False)


class YourCapitalPropertyForm(CheckerWizardMixin, forms.Form):
    worth = MoneyField(
        label=_(u"How much is it worth?"), required=True
    )
    mortgage_left = MoneyField(
        label=_(u"How much is left to pay on the mortgage?"),
        required=True
    )
    owner = RadioBooleanField(
        label=_(u"Is the property owned by you or is it in joint names?"),
        choices=OWNED_BY_CHOICES, required=True
    )
    share = forms.IntegerField(
        label=_(u'What is your share of the property?'),
        min_value=0, max_value=100
    )
    disputed = RadioBooleanField(
        label=_(u"Is this property disputed?"), required=True
    )


class YourCapitalSavingsForm(CheckerWizardMixin, forms.Form):
    bank = MoneyField(
        label=_(u"How much money do you have saved in a bank or building society?")
    )
    investments = MoneyField(
        label=_(u"What is the total value of any investments (shares or ISAs) you have?")
    )
    valuable_items = MoneyField(
        label=_(u"What is the total value of any items you have worth over £500?")
    )
    money_owed = MoneyField(
        label=_(u"How much money do you have owed to you?")
    )


class YourCapitalPartnerSavingsForm(CheckerWizardMixin, forms.Form):
    bank = MoneyField(
        label=_(u"How much money does your partner have saved in a bank or building society?")
    )
    investments = MoneyField(
        label=_(u"What is the total value of any investments (shares or ISAs) your partner has?")
    )
    valuable_items = MoneyField(
        label=_(u"What is the total value of any items your partner has worth over £500?")
    )
    money_owed = MoneyField(
        label=_(u"How much money does your partner have owed to them?")
    )


class OnlyAllowExtraIfNoInitialFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        if kwargs.get('initial'):
            self.extra = 0
        super(OnlyAllowExtraIfNoInitialFormSet, self).__init__(*args, **kwargs)

    def clean(self):
        from django.forms.util import ErrorList

        # if any form in error => skip
        if any([not form.is_valid() for form in self.forms]):
            return

        count = 0
        for form in self.forms:
            try:
                if form.cleaned_data:
                    count += 1
            except AttributeError:
                pass

        if count < self.total_form_count():
            raise forms.ValidationError(_('Fill in all your property details'))

        return self.cleaned_data

    def _get_form_index_from_prefix(self, key):
        key = key.lstrip(self.management_form.prefix)
        key = key.split('-')[-2]
        idx = int(key)
        return idx

    def _get_non_formset_data(self):
        return {k: v
                      for k, v in self.data.items()
                      if not re.match('%s-\d{1,2}-.*' % self.management_form.prefix,k ) }


    def _get_formset_data(self):
        return {k: v
                        for k, v in self.data.items()
                        if re.match('%s-\d{1,2}-.*' % self.management_form.prefix,k ) }

    def _get_grouped_formset_data(self, exclude=None):
        if not exclude:
            exclude = []

        grouped_formset_data = {}
        for i,g in itertools.groupby(sorted(self._get_formset_data().items()),
                                     lambda x:self._get_form_index_from_prefix(x[0])):
            if i not in exclude:
                grouped_formset_data[i] = list(g)
        return grouped_formset_data


    def remove_form(self, index):
        # remove the requested form
        self.forms.pop(index)


        # get non formset and keep it so we can set it to self.data
        other_data = self._get_non_formset_data()

        # fix the numbering of each remaining formset if required
        for i, (k, v) in enumerate(self._get_grouped_formset_data(exclude=[index]).items()):
            v = [(x[0].replace('-%s-' % k, '-%s-' % i), x[1]) for x in v]
            other_data.update(dict(v))

        self.data = other_data


        total_count_name = '%s-%s' % (self.management_form.prefix, TOTAL_FORM_COUNT)
        initial_count_name = '%s-%s' % (self.management_form.prefix, INITIAL_FORM_COUNT)
        self.data[total_count_name] = self.management_form.cleaned_data[TOTAL_FORM_COUNT] - 1
        self.data[initial_count_name] = self.management_form.cleaned_data[INITIAL_FORM_COUNT] - 1

        # remove the action from data
        self.data.pop('submit', None)

        # regenerate forms using updated data
        self.forms = [self._construct_form(i) for i in xrange(self.total_form_count())]

    def add_form(self, **kwargs):
        tfc = self.total_form_count()
        self.forms.append(self._construct_form(tfc, **kwargs))
        self.forms[tfc].is_bound = False

        # make data mutable
        self.data = self.data.copy()

        # increase hidden form counts
        total_count_name = '%s-%s' % (self.management_form.prefix, TOTAL_FORM_COUNT)
        initial_count_name = '%s-%s' % (self.management_form.prefix, INITIAL_FORM_COUNT)
        self.data[total_count_name] = self.management_form.cleaned_data[TOTAL_FORM_COUNT] + 1
        self.data[initial_count_name] = self.management_form.cleaned_data[INITIAL_FORM_COUNT] + 1

    @property
    def new_form_added(self):
        return self.data.get('submit') == 'add-property'

class YourCapitalForm(YourFinancesFormMixin, MultipleFormsForm):

    YourCapitalPropertyFormSet = formset_factory(
        YourCapitalPropertyForm,
        extra=1,
        max_num=20,
        validate_max=True,
        formset=OnlyAllowExtraIfNoInitialFormSet
    )

    formset_list = (
        ('property', YourCapitalPropertyFormSet),
    )

    forms_list = (
        ('your_savings', YourCapitalSavingsForm),
        ('partners_savings', YourCapitalPartnerSavingsForm),
    )

    def _prepare_for_init(self, kwargs):
        super(YourCapitalForm, self)._prepare_for_init(kwargs)

        new_forms_list = dict(self.forms_list)
        new_formset_list = dict(self.formset_list)
        if not self.has_partner:
            del new_forms_list['partners_savings']
        if not self.has_property:
            del new_formset_list['property']

        self.forms_list = new_forms_list.items()
        self.formset_list = new_formset_list.items()

    @property
    def total_capital_assets(self):
        return self._get_total_capital_assets(self.cleaned_data)

    def _get_total_capital_assets(self, cleaned_data):
        # used for display at the moment but maybe should come from a
        # common calculator lib so both front end and backend can share it

        total_of_savings = 0
        total_of_property = 0

        own_savings, partner_savings = self.get_savings(cleaned_data)
        total_of_savings = sum(itertools.chain(own_savings.values(), partner_savings.values()))

        properties = self.get_properties(cleaned_data)
        for property in properties:
            share = property['share']
            value = property['value']
            mortgage_left = property['mortgage_left']
            if share > 0:
                share = share / 100.0

                total_of_property +=  int(max(value - mortgage_left, 0) * share)

        return total_of_property + total_of_savings

    @property
    def cleaned_data(self):
        cleaned_data = super(YourCapitalForm, self).cleaned_data
        cleaned_data.update({
            'total_capital_assets': self._get_total_capital_assets(cleaned_data)
        })

        return cleaned_data

    def _get_savings(self, key, cleaned_data):
        if key in cleaned_data:
            return {
                'bank_balance': cleaned_data.get(key, {}).get('bank', 0),
                'asset_balance': cleaned_data.get(key, {}).get('valuable_items', 0),
                'credit_balance': cleaned_data.get(key, {}).get('money_owed', 0),
                'investment_balance': cleaned_data.get(key, {}).get('investments', 0),
            }

    def get_savings(self, cleaned_data):
        your_savings = self._get_savings('your_savings', cleaned_data)
        partner_savings = self._get_savings('partners_savings', cleaned_data) or {}
        return your_savings, partner_savings

    def get_properties(self, cleaned_data):
        def _transform(property):
            return {
                'mortgage_left': property.get('mortgage_left'),
                'share': property.get('share'),
                'value': property.get('worth'),
                'disputed': property.get('disputed')
            }
        properties = cleaned_data.get('property', [])
        return [_transform(p) for p in properties if p]

    def save(self):
        # eligibility check reference should be set otherwise => error
        self.check_that_reference_exists()

        data = self.cleaned_data
        your_savings, partner_savings = self.get_savings(data)
        post_data = {
            'property_set': self.get_properties(data),
            'you': {
                'savings': your_savings
            }
        }
        if partner_savings:
            post_data.update({
                'partner': {
                    'savings': partner_savings
                }
            })

        response = self.connection.eligibility_check(self.reference).patch(post_data)
        return {
            'eligibility_check': response
        }


    def process_actions(self):
        action = self.data.get('submit')
        property_formset = self.form_dict().get('property')
        if property_formset:
            if action == 'add-property':
                property_formset.add_form()
            if action and 'remove-property' in action:
                index = action.split('-')[-1]
                try:
                    index = int(index)
                    property_formset.remove_form(index)
                except ValueError:
                    pass
        return action != 'submit'

    @property
    def show_errors(self):
        for _, form in self.form_dict().items():
            if hasattr(form, 'new_form_added'):
                if form.new_form_added:
                    return False
        return True

class YourSingleIncomeForm(CheckerWizardMixin, forms.Form):
    earnings = MoneyIntervalField(
        label=_(u"Earnings last month"), min_value=0
    )

    other_income = MoneyIntervalField(
        label=_(u"Other income last month"), min_value=0
    )

    self_employed = RadioBooleanField(
        label=_(u"Are you self employed?"), initial=0
    )


class YourDependentsForm(CheckerWizardMixin, forms.Form):
    dependants_old = forms.IntegerField(
        label=_(u'Children aged 16 and over'), required=True,
        min_value=0, max_value=50
    )

    dependants_young = forms.IntegerField(
        label=_(u'Children aged 15 and under'), required=True,
        min_value=0, max_value=50
    )


class YourIncomeForm(YourFinancesFormMixin, MultipleFormsForm):
    forms_list = (
        ('your_income', YourSingleIncomeForm),
        ('partners_income', YourSingleIncomeForm),
        ('dependants', YourDependentsForm)
    )

    def _prepare_for_init(self, kwargs):
        super(YourIncomeForm, self)._prepare_for_init(kwargs)

        new_forms_list = dict(self.forms_list)
        if not self.has_partner:
            del new_forms_list['partners_income']
        if not self.has_children:
            del new_forms_list['dependants']

        self.forms_list = new_forms_list.items()

    def _get_total_earnings(self, cleaned_data):
        total = 0
        for i in self.get_incomes(cleaned_data):
            total += i['other_income']['per_month']
            total += i['earnings']['per_month']

        return total

    @property
    def total_earnings(self):
        return self._get_total_earnings(self.cleaned_data)

    @property
    def cleaned_data(self):
        cleaned_data = super(YourIncomeForm, self).cleaned_data
        cleaned_data.update({
            'total_earnings': self._get_total_earnings(cleaned_data)
        })

        return cleaned_data

    def get_income(self, key, cleaned_data):
        income = {
            'earnings': cleaned_data.get(key, {}).get('earnings', {'per_interval_value': 0, 'per_month': 0, 'interval_period': 'per_month'}),
            'other_income': cleaned_data.get(key, {}).get('other_income', {'per_interval_value': 0, 'per_month': 0, 'interval_period': 'per_month'}),
            'self_employed': cleaned_data.get(key, {}).get('self_employed', False)
        }

        return income

    def get_incomes(self, cleaned_data):
        your_income = self.get_income('your_income', cleaned_data)
        partner_income = self.get_income('partners_income', cleaned_data) or {}
        return your_income, partner_income

    def get_dependants(self, cleaned_data):
        return cleaned_data.get('dependants', {})

    def save(self):
        # eligibility check reference should be set otherwise => error
        self.check_that_reference_exists()

        data = self.cleaned_data
        your_income, partner_income = self.get_incomes(data)

        dependants = self.get_dependants(data)
        post_data = {
            'dependants_young': dependants.get('dependants_young', 0),
            'dependants_old': dependants.get('dependants_old', 0),
            'you': {
                'income': your_income
            }
        }
        if partner_income:
            post_data.update({
                'partner': {
                    'income': partner_income
                }
            })

        response = self.connection.eligibility_check(self.reference).patch(post_data)
        return {
            'eligibility_check': response
        }


class YourSingleAllowancesForm(CheckerWizardMixin, form_utils.forms.BetterForm):
    mortgage = MoneyIntervalField(label=_(u"Mortgage"), min_value=0)
    rent = MoneyIntervalField(label=_(u"Rent"), min_value=0)
    tax = MoneyIntervalField(label=_(u"Tax"), min_value=0)
    ni = MoneyIntervalField(label=_(u"National Insurance Contribution"), min_value=0)
    maintenance = MoneyIntervalField(label=_(u"Maintenance"), min_value=0)
    childcare = MoneyIntervalField(label=_(u"Childcare"), min_value=0)
    criminal_legalaid_contributions = MoneyField(
        label=_(u"Payments being made towards a contribution order"), min_value=0
    )

    class Meta:
        fieldsets = [('housing', {'fields': ['mortgage', 'rent'], 'legend': 'Housing costs', 'classes': ['FieldGroup']}),
                     ('', {'fields': ['tax', 'ni', 'maintenance', 'childcare', 'criminal_legalaid_contributions']})]


class YourAllowancesForm(YourFinancesFormMixin, MultipleFormsForm):
    forms_list = (
        ('your_allowances', YourSingleAllowancesForm),
        ('partners_allowances', YourSingleAllowancesForm)
    )

    def _prepare_for_init(self, kwargs):
        super(YourAllowancesForm, self)._prepare_for_init(kwargs)

        new_forms_list = dict(self.forms_list)
        if not self.has_partner:
            del new_forms_list['partners_allowances']

        self.forms_list = new_forms_list.items()

    def _get_allowances(self, key, cleaned_data):
        if key in cleaned_data:

            return {
                'mortgage': cleaned_data.get(key, {}).get('mortgage', {}),
                'rent': cleaned_data.get(key, {}).get('rent', {}),
                'income_tax': cleaned_data.get(key, {}).get('tax', {}),
                'national_insurance': cleaned_data.get(key, {}).get('ni', {}),
                'maintenance': cleaned_data.get(key, {}).get('maintenance', {}),
                'childcare': cleaned_data.get(key, {}).get('childcare', {}),
                'criminal_legalaid_contributions': cleaned_data.get(key, {}).get('criminal_legalaid_contributions', 0),
            }

    def get_allowances(self, cleaned_data):
        your_allowances = self._get_allowances('your_allowances', cleaned_data)
        partner_allowances = self._get_allowances('partners_allowances', cleaned_data) or {}
        return your_allowances, partner_allowances

    def save(self):
        # eligibility check reference should be set otherwise => error
        self.check_that_reference_exists()

        data = self.cleaned_data

        your_allowances, partner_allowances = self.get_allowances(data)
        post_data = {
            'you': {
                'deductions': your_allowances
            }
        }

        if partner_allowances:
            post_data.update({
                'partner': {
                    'deductions': partner_allowances
                }
            })

        response = self.connection.eligibility_check(self.reference).patch(post_data)
        return {
            'eligibility_check': response
        }
