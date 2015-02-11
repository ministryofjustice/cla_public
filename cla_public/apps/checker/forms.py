# -*- coding: utf-8 -*-
"Checker forms"

import logging

from flask import session, request
from flask_wtf import Form
from flask.ext.babel import lazy_gettext as _, lazy_pgettext
from werkzeug.datastructures import MultiDict
from wtforms import Form as NoCsrfForm
from wtforms.validators import InputRequired, NumberRange, DataRequired

from cla_public.apps.checker.constants import CATEGORIES, BENEFITS_CHOICES, \
    NON_INCOME_BENEFITS, YES, NO, PASSPORTED_BENEFITS
from cla_public.apps.checker.fields import (
    DescriptionRadioField, MoneyIntervalField,
    YesNoField, PartnerYesNoField, MoneyField,
    PartnerMoneyIntervalField, PartnerMultiCheckboxField, PartnerMoneyField,
    PropertyList,
    PassKwargsToFormField, SetZeroIntegerField, set_zero_values,
    SetZeroFormField)
from cla_public.apps.checker.utils import nass, passported, \
    money_intervals_except, money_intervals
from cla_public.apps.checker.validators import AtLeastOne, IgnoreIf, \
    FieldValue, MoneyIntervalAmountRequired, FieldValueOrNone
from cla_public.apps.base.forms import BabelTranslationsFormMixin
from cla_public.libs.honeypot import Honeypot
from cla_public.libs.form_config_parser import ConfigFormMixin
from cla_public.libs.money_interval import MoneyInterval
from cla_public.libs.utils import recursive_dict_update


log = logging.getLogger(__name__)


class FormSessionDataMixin(object):
    """
    Mixin for pre-populating the api payload with null or zero data
    Also loads session data if there is any available
    """

    @classmethod
    def get_session_data(cls):
        return session.get(cls.__name__, {})

    @classmethod
    def get_session_as_api_payload(cls):
        f = cls(MultiDict({}), cls.get_session_data())
        f.process()
        return f.api_payload()

    @classmethod
    def get_null_api_payload(cls):
        return cls().api_payload()

    @classmethod
    def get_zero_api_payload(cls):
        """
        Populate a form and nested forms with Zero values so if they don't
        need to be filled out
        """
        return set_zero_values(cls()).api_payload()


def update_payload(form_payload, form_class, cond=True):
    if cond:
        form_data = form_class.get_session_as_api_payload()
    else:
        form_data = form_class.get_zero_api_payload()
    recursive_dict_update(form_payload, form_data)


class ProblemForm(ConfigFormMixin, Honeypot, BabelTranslationsFormMixin, Form):
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


class AboutYouForm(Honeypot, BabelTranslationsFormMixin, Form):
    have_partner = YesNoField(
        _(u'Do you have a partner?'),
        description=(
            _(u"Your partner is your husband, wife, civil partner (unless "
              u"you have permanently separated) or someone you live with "
              u"as if you’re married")),
        yes_text=lazy_pgettext(u'There is/are', u'Yes'),
        no_text=lazy_pgettext(u'There is/are not', u'No'),
        )
    in_dispute = YesNoField(
        _(u'If Yes, are you in a dispute with your partner?'),
        description=(
            _(u"This means your partner is the opponent in the dispute "
              u"you need help with, for example a dispute over money or "
              u"property ")),
        validators=[
            IgnoreIf('have_partner', FieldValue(NO)),
            InputRequired(message=_(u'Please choose Yes or No'))
        ],
        yes_text=lazy_pgettext(u'I am', u'Yes'),
        no_text=lazy_pgettext(u'I’m not', u'No'))
    on_benefits = YesNoField(
        _(u'Do you receive any benefits (including Child Benefit)?'),
        description=(
            _(u"Being on some benefits can help you qualify for legal aid")),
        yes_text=lazy_pgettext(u'I am', u'Yes'),
        no_text=lazy_pgettext(u'I’m not', u'No'))
    have_children = YesNoField(
        _(u'Do you have any children aged 15 or under?'),
        description=_(u"Don't include any children who don't live with you"),
        yes_text=lazy_pgettext(u'There is/are', u'Yes'),
        no_text=lazy_pgettext(u'There is/are not', u'No'))
    num_children = SetZeroIntegerField(
        _(u'If Yes, how many?'),
        validators=[
            IgnoreIf('have_children', FieldValue(NO)),
            DataRequired(_(u'Number must be between 1 and 50')),
            NumberRange(min=1, max=50, message=_(
                u'Number must be between 1 and 50'))])
    have_dependants = YesNoField(
        _(u'Do you have any dependants aged 16 or over?'),
        description=_(
            u"People who you live with and support financially. This could be "
            u"a young person for whom you get Child Benefit"),
        yes_text=lazy_pgettext(u'There is/are', u'Yes'),
        no_text=lazy_pgettext(u'There is/are not', u'No'))
    num_dependants = SetZeroIntegerField(
        _(u'If Yes, how many?'),
        validators=[
            IgnoreIf('have_dependants', FieldValue(NO)),
            DataRequired(_(u'Number must be between 1 and 50')),
            NumberRange(min=1, max=50, message=_(
                u'Number must be between 1 and 50'))])
    have_savings = YesNoField(
        _(u'Do you have any savings or investments?'),
        yes_text=lazy_pgettext(u'There is/are', u'Yes'),
        no_text=lazy_pgettext(u'There is/are not', u'No'))
    have_valuables = YesNoField(
        _(u'Do you have any valuable items worth over £500 each?'),
        yes_text=lazy_pgettext(u'There is/are', u'Yes'),
        no_text=lazy_pgettext(u'There is/are not', u'No'))
    own_property = YesNoField(
        _(u'Do you own any property?'),
        description=_(u"For example, a house, static caravan or flat"))
    is_employed = YesNoField(
        _(u'Are you employed?'),
        description=(
            _(u"This means working as an employee - you may be both employed "
              u"and self-employed")),
        yes_text=lazy_pgettext(u'I am', u'Yes'),
        no_text=lazy_pgettext(u'I’m not', u'No'))
    partner_is_employed = YesNoField(
        _(u'Is your partner employed?'),
        description=_(
            u"This means working as an employee - your partner may be both "
            u"employed and self-employed"),
        validators=[
            IgnoreIf('in_dispute', FieldValueOrNone(YES)),
            InputRequired(message=_(u'Please choose Yes or No'))],
        yes_text=lazy_pgettext(u'There is/are', u'Yes'),
        no_text=lazy_pgettext(u'There is/are not', u'No'))
    is_self_employed = YesNoField(
        _(u'Are you self-employed?'),
        description=(
            _(u"This means working for yourself - you may be both employed "
              u"and self-employed")),
        yes_text=lazy_pgettext(u'I am', u'Yes'),
        no_text=lazy_pgettext(u'I’m not', u'No'))
    partner_is_self_employed = YesNoField(
        _(u'Is your partner self-employed?'),
        description=_(
            u"This means working for yourself - your partner may be both "
            u"employed and self-employed"),
        validators=[
            IgnoreIf('in_dispute', FieldValueOrNone(YES)),
            InputRequired(message=_(u'Please choose Yes or No'))],
        yes_text=lazy_pgettext(u'There is/are', u'Yes'),
        no_text=lazy_pgettext(u'There is/are not', u'No'))
    aged_60_or_over = YesNoField(
        _(u'Are you or your partner (if you have one) aged 60 or over?'),
        yes_text=lazy_pgettext(u'I am', u'Yes'),
        no_text=lazy_pgettext(u'I’m not', u'No'))

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

        update_payload(payload, PropertiesForm, cond=self.require_properties)
        update_payload(payload, SavingsForm, cond=self.require_savings)
        update_payload(payload, IncomeForm)
        update_payload(payload, OutgoingsForm)

        return payload

    @property
    def require_properties(self):
        return self.own_property.data == YES

    @property
    def require_savings(self):
        return self.have_savings.data == YES or self.have_valuables.data == YES


class YourBenefitsForm(ConfigFormMixin, Honeypot, BabelTranslationsFormMixin, Form):
    benefits = PartnerMultiCheckboxField(
        label=_(u'Are you on any of these benefits?'),
        partner_label=_(u'Are you or your partner on any of these benefits?'),
        choices=BENEFITS_CHOICES,
        validators=[AtLeastOne()])

    def api_payload(self):
        is_selected = lambda benefit: benefit in self.benefits.data
        as_tuple = lambda benefit: (benefit, is_selected(benefit))
        benefits = dict(map(as_tuple, PASSPORTED_BENEFITS))
        payload = {
            'specific_benefits': benefits,
            'on_passported_benefits': passported(self.benefits.data)
        }

        if passported(self.benefits.data):
            update_payload(payload, IncomeForm, cond=False)
            update_payload(payload, OutgoingsForm, cond=False)

        return payload


class PropertyForm(BabelTranslationsFormMixin, NoCsrfForm, FormSessionDataMixin):
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
            u'of the property?'),
        yes_text=lazy_pgettext(u'There is/are', u'Yes'),
        no_text=lazy_pgettext(u'There is/are not', u'No'))
    property_value = MoneyField(
        _(u'How much is the property worth?'),
        description=_(
            u"Use a property website or the Land Registry house prices "
            u"website."),
        validators=[
            InputRequired(_(u'Please enter a valid amount'))])
    mortgage_remaining = MoneyField(
        _(u'How much is left to pay on the mortgage?'),
        description=(
            _(u"Include the full amount owed, even if the property has "
              u"shared ownership")),
        validators=[
            InputRequired(_(u'Please enter 0 if you have no mortgage'))])
    mortgage_payments = MoneyField(
        _(u'How much are your monthly mortgage repayments?'),
        validators=[IgnoreIf('mortgage_remaining', FieldValue(0))])
    is_rented = YesNoField(
        _(u'Do you rent out any part of this property?'),
        yes_text=lazy_pgettext(u'I am', u'Yes'),
        no_text=lazy_pgettext(u'I’m not', u'No'))
    rent_amount = MoneyIntervalField(
        _(u'If Yes, how much rent do you receive?'),
        choices=money_intervals_except('per_4week'),
        validators=[
            IgnoreIf('is_rented', FieldValue(NO)),
            MoneyIntervalAmountRequired()])
    in_dispute = YesNoField(
        _(u'Is your share of the property in dispute?'),
        description=_(
            u"For example, as part of the financial settlement of a divorce"),
        yes_text=lazy_pgettext(u'There is/are', u'Yes'),
        no_text=lazy_pgettext(u'There is/are not', u'No'))

    def api_payload(self):
        share = 100 if self.other_shareholders.data == NO else None
        return {
            'value': self.property_value.data,
            'mortgage_left': self.mortgage_remaining.data,
            'share': share,
            'disputed': self.in_dispute.data,
            'rent': self.rent_amount.data if self.is_rented.data == YES else MoneyInterval(0),
            'main': self.is_main_home.data
        }


class PropertiesForm(ConfigFormMixin, Honeypot, BabelTranslationsFormMixin, Form, FormSessionDataMixin):
    properties = PropertyList(
        SetZeroFormField(PropertyForm), min_entries=1, max_entries=3)

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
        total_rent = sum(rents, MoneyInterval(0))

        total_mortgage = sum(
            [p.mortgage_payments.data for p in self.properties
                if p.mortgage_payments.data is not None]
        )
        return {
            'property_set': properties,
            'you': {
                'income': {'other_income': total_rent},
                'deductions': {
                    'mortgage': MoneyInterval(total_mortgage, 'per_month')}
            }
        }


class SavingsForm(ConfigFormMixin, Honeypot, BabelTranslationsFormMixin, Form, FormSessionDataMixin):
    savings = MoneyField(
        _('Savings'),
        description=_(
            u"The total amount of savings in cash, bank or building society"),
        validators=[InputRequired(
            message=_(u'Enter 0 if you have no savings')
        )])
    investments = MoneyField(
        _('Investments'),
        description=_(
            u"This includes stocks, shares, bonds (but not property)"),
        validators=[InputRequired(
            message=_(u'Enter 0 if you have no investments')
        )])
    valuables = MoneyField(
        _(u'Total value of items worth over £500 each'),
        min_val=50000,
        validators=[InputRequired(
            message=_(u'Valuable items must be at least £500')
        )])

    def __init__(self, *args, **kwargs):
        super(SavingsForm, self).__init__(*args, **kwargs)

        if not session.has_valuables:
            del self.valuables

        if not session.has_savings:
            del self.savings
            del self.investments

    def api_payload(self):
        return {'you': {'savings': {
            'bank_balance': self.savings.data if self.savings else 0,
            'investment_balance': self.investments.data if self.investments else 0,
            'asset_balance': self.valuables.data if self.valuables else 0
        }}}


class TaxCreditsForm(ConfigFormMixin, Honeypot, BabelTranslationsFormMixin, Form):
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
        partner_label=_(u'Do you or your partner receive any other benefits '
                        u'not listed above? '),
        description=_(u'For example, National Asylum Support Service Benefit, '
                      u'Incapacity Benefit, Contribution-based Jobseeker\'s '
                      u'Allowance'),
        yes_text=lazy_pgettext(u'I am', u'Yes'),
        no_text=lazy_pgettext(u'I’m not', u'No'))
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
                self.other_benefits.data == YES else MoneyInterval(0)
            }}
        }


class IncomeFieldForm(BabelTranslationsFormMixin, NoCsrfForm, FormSessionDataMixin):

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
            'TaxCreditsForm_child_tax_credit', MoneyInterval(0))
        if not self.is_partner:
            tax_credits = tax_credits + child_tax_credit

        is_self_employed = session.is_self_employed
        is_employed = session.is_employed
        if self.is_partner:
            is_self_employed = session.partner_is_self_employed
            is_employed = session.partner_is_employed

        earnings = self.earnings.data
        self_employed_drawings = MoneyInterval(0)
        # Switch all earnings to self employed drawings if only self employed
        if is_self_employed and not is_employed:
            earnings, self_employed_drawings = self_employed_drawings, earnings

        other_income = self.other_income.data
        if session.owns_property:
            rents = [p['rent_amount'] for p in session.get(
                'PropertiesForm_properties', [])]
            total_rent = sum(rents, MoneyInterval(0))
            other_income = other_income + total_rent

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


class IncomeForm(ConfigFormMixin, Honeypot, BabelTranslationsFormMixin, Form, FormSessionDataMixin):
    your_income = SetZeroFormField(IncomeFieldForm, label=_(u'Your personal income'))
    partner_income = PassKwargsToFormField(
        IncomeFieldForm,
        form_kwargs={'is_partner': True},
        label=_(u'Your partner’s income'))

    def __init__(self, *args, **kwargs):
        """Dynamically remove partner subform if user has no partner"""
        super(IncomeForm, self).__init__(*args, **kwargs)
        if not session.has_partner:
            del self.partner_income

    def api_payload(self):
        api_payload = {
            'you': self.your_income.form.api_payload(),
        }
        partner_income = getattr(self, 'partner_income', None)
        if partner_income:
            api_payload['partner'] = partner_income.form.api_payload()

        return api_payload


class OutgoingsForm(ConfigFormMixin, Honeypot, BabelTranslationsFormMixin,
                    Form, FormSessionDataMixin):
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
