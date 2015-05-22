# -*- coding: utf-8 -*-
"Checker forms"

import logging

from flask import session, request
from flask_wtf import Form
from flask.ext.babel import lazy_gettext as _, lazy_pgettext
from werkzeug.datastructures import MultiDict
from wtforms import Form as NoCsrfForm, StringField, RadioField
from wtforms.validators import InputRequired, NumberRange, DataRequired

from cla_public.apps.checker.api import money_interval
from cla_public.apps.checker.constants import CATEGORIES, BENEFITS_CHOICES, \
    NON_INCOME_BENEFITS, YES, NO, PASSPORTED_BENEFITS, LEGAL_ADVISER_SEARCH_PREFERENCE
from cla_public.apps.checker.fields import (
    DescriptionRadioField, MoneyIntervalField,
    YesNoField, PartnerYesNoField, MoneyField,
    PartnerMoneyIntervalField, PartnerMultiCheckboxField, PartnerMoneyField,
    PropertyList, money_interval_to_monthly,
    PassKwargsToFormField, SetZeroIntegerField, set_zero_values,
    SetZeroFormField)
from cla_public.libs.form_config_parser import ConfigFormMixin
from cla_public.libs.honeypot import Honeypot
from cla_public.apps.checker.utils import nass, passported, \
    money_intervals_except, money_intervals
from cla_public.apps.checker.validators import AtLeastOne, IgnoreIf, \
    FieldValue, MoneyIntervalAmountRequired, FieldValueOrNone, ZeroOrMoreThan
from cla_public.libs.utils import recursive_dict_update, classproperty
from cla_public.apps.base.forms import BabelTranslationsFormMixin


log = logging.getLogger(__name__)


class BaseForm(BabelTranslationsFormMixin, Honeypot, Form):
    pass


class BaseNoCsrfForm(BabelTranslationsFormMixin, NoCsrfForm):
    pass


class AboutYouForm(BaseForm):

    title = _(u'About you')
    have_partner = YesNoField(
        _(u'Do you have a partner?'),
        description=(
            _(u"Your husband, wife, civil partner (unless "
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


class YourBenefitsForm(BaseForm):

    @classproperty
    def title(self):
        if session and session.checker.has_partner:
            return _(u'You and your partner’s benefits')
        return _(u'Your benefits')

    benefits = PartnerMultiCheckboxField(
        label=_(u'Are you on any of these benefits?'),
        partner_label=_(u'Are you or your partner on any of these benefits?'),
        choices=BENEFITS_CHOICES,
        validators=[AtLeastOne()])


class PropertyForm(BaseNoCsrfForm):

    is_main_home = YesNoField(
        _(u'Is this property your main home?'),
        description=(
            _(u"If you are separated and no longer live in the property you "
              u"own, please answer ‘no’")))
    other_shareholders = PartnerYesNoField(
        label=_(
            u'Does anyone else own a share of the property?'),
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
        _(u'How much was your monthly mortgage repayment last month?'),
        validators=[IgnoreIf('mortgage_remaining', FieldValue(0))])
    is_rented = YesNoField(
        _(u'Do you rent out any part of this property?'),
        yes_text=lazy_pgettext(u'I am', u'Yes'),
        no_text=lazy_pgettext(u'I’m not', u'No'))
    rent_amount = MoneyIntervalField(
        _(u'If Yes, how much rent did you receive last month?'),
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


class PropertiesForm(BaseForm):

    @classproperty
    def title(self):
        if session and session.checker.has_partner:
            return _(u'You and your partner’s property')
        return _(u'Your property')

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


class SavingsForm(BaseForm):

    @classproperty
    def title(self):
        if session and session.checker.has_partner:
            return _(u'You and your partner’s savings')
        return _(u'Your savings')

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
        validators=[
            InputRequired(message=_(
                u'Enter 0 if you have no valuable items worth over £500 each'
            )),
            ZeroOrMoreThan(50000)
        ])

    def __init__(self, *args, **kwargs):
        super(SavingsForm, self).__init__(*args, **kwargs)

        if not session.checker.has_valuables:
            del self.valuables

        if not session.checker.has_savings:
            del self.savings
            del self.investments


class TaxCreditsForm(BaseForm):

    @classproperty
    def title(self):
        if session and session.checker.has_partner:
            return _(u'You and your partner’s benefits and tax credits')
        return _(u'Your benefits and tax credits')

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


class IncomeFieldForm(BaseNoCsrfForm):

    def __init__(self, *args, **kwargs):
        self.is_partner = kwargs.pop('is_partner', False)
        super(IncomeFieldForm, self).__init__(*args, **kwargs)
        if (not (session.checker.is_employed or session.checker.is_self_employed) and not self.is_partner) or \
           (not (session.checker.partner_is_employed or session.checker.partner_is_self_employed) and self.is_partner):
            del self.earnings
            del self.income_tax
            del self.national_insurance
            del self.working_tax_credit

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


class IncomeField(PassKwargsToFormField):

    def __init__(self, *args, **kwargs):
        super(IncomeField, self).__init__(
            IncomeFieldForm,
            *args, **kwargs)


class IncomeForm(BaseForm):

    @classproperty
    def title(self):
        has_partner = session and session.checker.has_partner
        employed = session and (session.checker.is_employed or session.checker.is_self_employed)
        if has_partner:
            if employed:
                return _(u'You and your partner’s income and tax')
            return _(u'You and your partner’s money coming in')
        elif employed:
            return _(u'Your income and tax')
        return _(u'Your money coming in')

    your_income = IncomeField(label=_(u'Your personal income'))
    partner_income = IncomeField(
        form_kwargs={'is_partner': True},
        label=_(u'Your partner’s income'))

    def __init__(self, *args, **kwargs):
        """Dynamically remove partner subform if user has no partner"""
        super(IncomeForm, self).__init__(*args, **kwargs)
        if not session.checker.has_partner:
            del self.partner_income


class OutgoingsForm(BaseForm):

    @classproperty
    def title(self):
        if session and session.checker.has_partner:
            return _(u'You and your partner’s outgoings')
        return _(u'Your outgoings')

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

    def __init__(self, *args, **kwargs):
        super(OutgoingsForm, self).__init__(*args, **kwargs)
        if not session.checker.has_children and not session.checker.has_dependants:
            del self.childcare


class ReviewForm(BaseForm):
    title = _(u'Review your answers')


class FindLegalAdviserForm(Honeypot, BabelTranslationsFormMixin, Form):
    postcode = StringField(
        _(u'Enter postcode'),
        validators=[InputRequired()]
    )
