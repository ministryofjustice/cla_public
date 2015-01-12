# -*- coding: utf-8 -*-
"Checker forms"

import logging

from flask import session, request
from flask_wtf import Form
from flask.ext.babel import lazy_gettext as _, gettext
from wtforms import Form as NoCsrfForm
from wtforms import IntegerField, FormField
from wtforms.validators import InputRequired, NumberRange

from cla_public.apps.checker.api import money_interval
from cla_public.apps.checker.constants import CATEGORIES, BENEFITS_CHOICES, \
    NON_INCOME_BENEFITS, YES, NO, PASSPORTED_BENEFITS
from cla_public.apps.checker.fields import (
    DescriptionRadioField, MoneyIntervalField,
    YesNoField, PartnerYesNoField, MoneyField,
    PartnerMoneyIntervalField, PartnerMultiCheckboxField, PartnerMoneyField,
    PropertyList, money_interval_to_monthly,
    PassKwargsToFormField)
from cla_public.libs.form_config_parser import ConfigFormMixin
from cla_public.libs.honeypot import Honeypot
from cla_public.apps.checker.utils import nass, passported, \
    money_intervals_except, money_intervals
from cla_public.apps.checker.validators import AtLeastOne, IgnoreIf, \
    FieldValue, MoneyIntervalAmountRequired, FieldValueOrNone


log = logging.getLogger(__name__)


class ProblemForm(ConfigFormMixin, Honeypot, Form):
    """Area of law choice"""

    categories = DescriptionRadioField(
        _(u'What do you need help with?'),
        choices=CATEGORIES,
        coerce=unicode,
        validators=[InputRequired()])

    def api_payload(self):
        category = self.categories.data
        if category == 'violence':
            category = 'family'
        session.add_note(u'User selected category: {0}'.format(
            self.categories.data))
        return {
            'category': category
        }


class AboutYouForm(ConfigFormMixin, Honeypot, Form):
    have_partner = YesNoField(
        _(u'Do you have a partner?'),
        description=(
            _(u"Your partner is your husband, wife, civil partner (unless "
              u"you have permanently separated) or someone you live with "
              u"as if you’re married")))
    in_dispute = YesNoField(
        _(u'If Yes, are you in a dispute with your partner?'),
        description=(
            _(u"This means your partner is the opponent in the dispute "
              u"you need help with, for example a dispute over money or "
              u"property ")),
        validators=[
            IgnoreIf('have_partner', FieldValue(NO)),
            InputRequired(message=gettext(u'Please choose Yes or No'))
        ])
    on_benefits = YesNoField(
        _(u'Do you receive any benefits (including Child Benefit)?'),
        description=(
            _(u"Being on some benefits can help you qualify for legal aid")))
    have_children = YesNoField(
        _(u'Do you have any children aged 15 or under?'),
        description=_(u"Don't include any children who don't live with you"))
    num_children = IntegerField(
        _(u'If Yes, how many?'),
        validators=[
            IgnoreIf('have_children', FieldValue(NO)),
            NumberRange(min=1)])
    have_dependants = YesNoField(
        _(u'Do you have any dependants aged 16 or over?'),
        description=_(
            u"People who you live with and support financially. This could be "
            u"a young person for whom you get Child Benefit"))
    num_dependants = IntegerField(
        _(u'If Yes, how many?'),
        validators=[
            IgnoreIf('have_dependants', FieldValue(NO)),
            NumberRange(min=1)])
    have_savings = YesNoField(
        _(u'Do you have any savings or investments?'))
    have_valuables = YesNoField(
        _(u'Do you have any valuable items worth over £500 each?'))
    own_property = YesNoField(
        _(u'Do you own any property?'),
        description=_(u"For example, a house, static caravan or flat"))
    is_employed = YesNoField(
        _(u'Are you employed?'),
        description=(
            _(u"This means working as an employee - you may be both employed "
              u"and self-employed")))
    partner_is_employed = YesNoField(
        _(u'Is your partner employed?'),
        description=_(
            u"This means working as an employee - your partner may be both "
            u"employed and self-employed"),
        validators=[
            IgnoreIf('in_dispute', FieldValueOrNone(YES)),
            InputRequired(message=gettext(u'Please choose Yes or No'))])
    is_self_employed = YesNoField(
        _(u'Are you self-employed?'),
        description=(
            _(u"This means working for yourself - you may be both employed "
              u"and self-employed")))
    partner_is_self_employed = YesNoField(
        _(u'Is your partner self-employed?'),
        description=_(
            u"This means working for yourself - your partner may be both "
            u"employed and self-employed"),
        validators=[
            IgnoreIf('in_dispute', FieldValueOrNone(YES)),
            InputRequired(message=gettext(u'Please choose Yes or No'))])
    aged_60_or_over = YesNoField(_(u'Are you or your partner aged 60 or over?'))

    def api_payload(self):
        def value_or_zero(field, dependant_field):
            if dependant_field.data == YES and field.data:
                return field.data
            return 0

        payload = {
            'dependants_young': value_or_zero(self.num_children, self.have_children),
            'dependants_old': value_or_zero(self.num_dependants, self.have_dependants),
            'is_you_or_your_partner_over_60': self.aged_60_or_over.data,
            'has_partner': self.have_partner.data,
            'you': {'income': {
                'self_employed': self.is_self_employed.data}}
        }

        if self.have_partner.data == YES and self.in_dispute.data != YES \
                and self.partner_is_self_employed.data == YES:
            payload['partner'] = {'income': {
                'self_employed': self.partner_is_self_employed.data}}
        return payload


class YourBenefitsForm(ConfigFormMixin, Honeypot, Form):
    benefits = PartnerMultiCheckboxField(
        label=_(u'Are you on any of these benefits?'),
        partner_label=_(u'Are you or your partner on any of these benefits?'),
        choices=BENEFITS_CHOICES,
        validators=[AtLeastOne()])

    def api_payload(self):
        is_selected = lambda benefit: benefit in self.benefits.data
        as_tuple = lambda benefit: (benefit, is_selected(benefit))
        benefits = dict(map(as_tuple, PASSPORTED_BENEFITS))
        return {
            'specific_benefits': benefits,
            'on_passported_benefits': passported(self.benefits.data)
        }


class PropertyForm(NoCsrfForm):
    is_main_home = YesNoField(
        _(u'Is this property your main home?'),
        description=(
            _(u"If you are separated and no longer live in the property you "
              u"own, please answer ‘no’")))
    other_shareholders = PartnerYesNoField(
        label=_(
            u'Does anyone else (other than you) own a share of the property?'),
        description=_(
            u"Select 'Yes' if you share ownership with a friend, relative or "
            u"ex-partner"),
        partner_label=_(
            u'Does anyone else (other than you or your partner) own a share '
            u'of the property?'))
    property_value = MoneyField(
        _(u'How much is the property worth?'),
        description=_(
            u"Use a property website or the Land Registry house prices "
            u"website."),
        validators=[
            InputRequired(gettext(u'Please enter a valid amount')),
            NumberRange(min=0)])
    mortgage_remaining = MoneyField(
        _(u'How much is left to pay on the mortgage?'),
        description=(
            _(u"Include the full amount owed, even if the property has "
              u"shared ownership")),
        validators=[
            InputRequired(gettext(u'Please enter 0 if you have no mortgage')),
            NumberRange(min=0)])
    mortgage_payments = MoneyField(
        _(u'How much are your monthly mortgage repayments?'),
        validators=[
            IgnoreIf('mortgage_remaining', FieldValue(0)),
            NumberRange(min=0)])
    is_rented = YesNoField(_(u'Do you rent out any part of this property?'))
    rent_amount = MoneyIntervalField(
        _(u'If Yes, how much rent do you receive?'),
        choices=money_intervals_except('per_4week'),
        validators=[
            IgnoreIf('is_rented', FieldValue(NO)),
            MoneyIntervalAmountRequired()])
    in_dispute = YesNoField(
        _(u'Is your share of the property in dispute?'),
        description=_(
            u"For example, as part of the financial settlement of a divorce"))

    def api_payload(self):
        share = 100 if self.other_shareholders.data == NO else None
        return {
            'value': self.property_value.data,
            'mortgage_left': self.mortgage_remaining.data,
            'share': share,
            'disputed': self.in_dispute.data,
            'rent': self.rent_amount.data if self.is_rented.data == YES else money_interval(0),
            'main': self.is_main_home.data
        }


def sum_money_intervals(first, second):
    first = money_interval_to_monthly(first)
    second = money_interval_to_monthly(second)
    return money_interval(
        first['per_interval_value'] + second['per_interval_value'],
        first['interval_period'])


def sum_rents(rents):
    return reduce(sum_money_intervals, rents, money_interval(0))


class PropertiesForm(ConfigFormMixin, Honeypot, Form):
    properties = PropertyList(
        FormField(PropertyForm), min_entries=1, max_entries=3)

    _submitted = None

    def is_submitted(self):
        if self._submitted is None:
            if 'add-property' in request.form:
                if len(self.properties.entries) < self.properties.max_entries:
                    self.properties.append_entry()
                self._submitted = False
            elif 'remove-property-1' in request.form:
                self.properties.remove(1)
                self._submitted = False
            elif 'remove-property-2' in request.form:
                self.properties.remove(2)
                self._submitted = False
            else:
                self._submitted = super(PropertiesForm, self).is_submitted()
        return self._submitted

    def api_payload(self):
        properties = [prop.form.api_payload() for prop in self.properties]
        rents = [prop['rent'] for prop in properties]
        total_rent = sum_rents(rents)

        total_mortgage = sum(
            [p.mortgage_payments.data for p in self.properties
                if p.mortgage_payments.data is not None]
        )
        return {
            'property_set': properties,
            'you': {
                'income': {'other_income': total_rent},
                'deductions': {
                    'mortgage': money_interval(total_mortgage, 'per_month')}
            }
        }


class SavingsForm(ConfigFormMixin, Honeypot, Form):
    savings = MoneyField(
        description=_(
            u"The total amount of savings in cash, bank or building society"),
        validators=[InputRequired(
            message=gettext(u'Enter 0 if you have no savings')
        )])
    investments = MoneyField(
        description=_(
            u"This includes stocks, shares, bonds (but not property)"),
        validators=[InputRequired(
            message=gettext(u'Enter 0 if you have no investments')
        )])
    valuables = MoneyField(
        _(u'Total value of items worth over £500 each'))

    def api_payload(self):
        # rather than showing an error message, just ignore values less than
        # £500
        valuables = self.valuables.data
        if valuables < 50000:
            valuables = 0
        return {'you': {'savings': {
            'bank_balance': self.savings.data,
            'investment_balance': self.investments.data,
            'asset_balance': valuables
        }}}


class TaxCreditsForm(ConfigFormMixin, Honeypot, Form):
    child_benefit = MoneyIntervalField(
        _(u'Child Benefit'),
        description=_(u"The total amount you get for all your children"),
        choices=money_intervals('', 'per_week', 'per_4week'),
        validators=[MoneyIntervalAmountRequired()])
    child_tax_credit = MoneyIntervalField(
        _(u'Child Tax Credit'),
        description=_(u"The total amount you get for all your children"),
        choices=money_intervals_except('per_month'),
        validators=[MoneyIntervalAmountRequired()])
    benefits = PartnerMultiCheckboxField(
        label=_(u'Do you get any of these benefits?'),
        partner_label=_(u'Do you or your partner get any of these benefits?'),
        description=_(u"These benefits don’t count as income. Please tick "
                      u"the ones you receive."),
        choices=NON_INCOME_BENEFITS)
    other_benefits = PartnerYesNoField(
        label=_(u'Do you receive any other benefits not listed above? '),
        partner_label=_(
            u'Do you or your partner receive any other benefits not listed '
            u'above? '),
        description=_(
            u'For example, Incapacity Benefit, Contribution-based '
            u'Jobseeker\'s Allowance'))
    total_other_benefit = MoneyIntervalField(
        _(u'If Yes, total amount of benefits not listed above'),
        choices=money_intervals_except('per_month'),
        validators=[
            IgnoreIf('other_benefits', FieldValue(NO)),
            MoneyIntervalAmountRequired()])

    def api_payload(self):
        session.add_note(u'Other benefits:\n{0}'.format('\n'.join([
            u' - {0}'.format(benefit) for benefit in self.benefits.data])))
        return {
            'on_nass_benefits': nass(self.benefits.data),
            'you': {'income': {
                'child_benefits': self.child_benefit.data,
                'tax_credits': self.child_tax_credit.data,
                'benefits': self.total_other_benefit.data if
                self.other_benefits.data == YES else money_interval(0)
            }}
        }


class IncomeFieldForm(NoCsrfForm):

    def __init__(self, *args, **kwargs):
        self.is_partner = kwargs.pop('is_partner', False)
        super(IncomeFieldForm, self).__init__(*args, **kwargs)

    earnings = MoneyIntervalField(
        _(u'Wages before tax'),
        description=(
            _(u"This includes all your wages and any earnings from "
              u"self-employment")),
        validators=[MoneyIntervalAmountRequired()])
    income_tax = MoneyIntervalField(
        _(u'Income tax'),
        description=(
            _(u"Tax paid directly out of your wages and any tax you pay on "
              u"self-employed earnings")),
        validators=[MoneyIntervalAmountRequired()])
    national_insurance = MoneyIntervalField(
        _(u'National Insurance contributions'),
        description=(
            _(u"Check your payslip or your National Insurance statement if "
              u"you’re self-employed")),
        validators=[MoneyIntervalAmountRequired()])
    working_tax_credit = MoneyIntervalField(
        _(u'Working Tax Credit'),
        description=_(
            u'Extra money for people who work and have a low income'),
        validators=[MoneyIntervalAmountRequired()])
    maintenance = MoneyIntervalField(
        _(u'Maintenance received'),
        description=_(u"Payments you get from an ex-partner"),
        validators=[MoneyIntervalAmountRequired()])
    pension = MoneyIntervalField(
        _(u'Pension received'),
        description=_(u"Payments you receive if you’re retired"),
        validators=[MoneyIntervalAmountRequired()])
    other_income = MoneyIntervalField(
        _(u'Any other income'),
        description=_(
            u"For example, student grants, income from trust funds, "
            u"dividends"),
        validators=[MoneyIntervalAmountRequired()])

    def api_payload(self):
        tax_credits = self.working_tax_credit.data
        child_tax_credit = session.get(
            'TaxCreditsForm_child_tax_credit', money_interval(0))
        if not self.is_partner:
            tax_credits = sum_money_intervals(tax_credits, child_tax_credit)

        is_self_employed = session.is_self_employed
        is_employed = session.is_employed
        if self.is_partner:
            is_self_employed = session.partner_is_self_employed
            is_employed = session.partner_is_employed

        earnings = self.earnings.data
        self_employed_drawings = money_interval(0)
        # Switch all earnings to self employed drawings if only self employed
        if is_self_employed and not is_employed:
            earnings, self_employed_drawings = self_employed_drawings, earnings

        other_income = self.other_income.data
        if session.owns_property:
            rents = [p['rent_amount'] for p in session.get(
                'PropertiesForm_properties', [])]
            total_rent = sum_rents(rents)
            other_income = sum_money_intervals(other_income, total_rent)

        return {
            'income': {
                'earnings': earnings,
                'self_employment_drawings': self_employed_drawings,
                'tax_credits': tax_credits,
                'maintenance_received': self.maintenance.data,
                'pension': self.pension.data,
                'other_income': other_income
            },
            'deductions': {
                'income_tax': self.income_tax.data,
                'national_insurance': self.national_insurance.data,
            }
        }


class IncomeAndTaxForm(ConfigFormMixin, Honeypot, Form):
    your_income = FormField(IncomeFieldForm, label=_(u'Your personal income'))

    def api_payload(self):
        api_payload = {
            'you': self.your_income.form.api_payload(),
        }
        partner_income = getattr(self, 'partner_income', None)
        if partner_income:
            api_payload['partner'] = partner_income.form.api_payload()

        return api_payload


def income_form(*args, **kwargs):
    """Dynamically add partner subform if user has a partner"""

    class IncomeForm(IncomeAndTaxForm):
        pass

    if session.has_partner:
        IncomeForm.partner_income = PassKwargsToFormField(
            IncomeFieldForm,
            form_kwargs={'is_partner': True},
            label=_(u'Your partner‘s income'))

    return IncomeForm(*args, **kwargs)


class OutgoingsForm(ConfigFormMixin, Honeypot, Form):
    rent = PartnerMoneyIntervalField(
        label=_(u'Rent'),
        description=_(u"Money you pay your landlord for rent. Do not include "
                      u"rent that is paid by Housing Benefit"),
        partner_description=_(u"Money you and your partner pay your landlord "
                              u"for rent. Do not include rent that is paid by "
                              u"Housing Benefit"),
        choices=money_intervals_except('per_4week'),
        validators=[MoneyIntervalAmountRequired()])
    maintenance = PartnerMoneyIntervalField(
        label=_(u'Maintenance'),
        description=_(
            u"Money you pay to an ex-partner for their living costs"),
        partner_description=_(u"Money you and/or your partner pay to an "
                              u"ex-partner for their living costs"),
        validators=[MoneyIntervalAmountRequired()])
    income_contribution = PartnerMoneyField(
        label=_(u'Monthly Income Contribution Order'),
        description=_(
            u"Money you pay per month towards your criminal legal aid"),
        partner_description=_(u"Money you and/or your partner pay per month "
                              u"towards your criminal legal aid"))
    childcare = PartnerMoneyIntervalField(
        label=_(u'Childcare'),
        description=_(
            u"Money you pay for your child to be looked after while "
            u"you work or study outside of your home"),
        partner_description=_(
            u"Money you and your partner pay for your child to "
            u"be looked after while you work or study outside "
            u"of your home"),
        choices=money_intervals_except('per_4week'),
        validators=[MoneyIntervalAmountRequired()])

    def api_payload(self):
        return {'you': {'deductions': {
            'rent': self.rent.data,
            'maintenance': self.maintenance.data,
            'criminal_legalaid_contributions':
                self.income_contribution.data,
            'childcare': self.childcare.data
        }}}
