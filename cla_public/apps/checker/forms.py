# -*- coding: utf-8 -*-
"Checker forms"

import logging

from flask import current_app, session, request
from flask_wtf import Form
import pytz

from wtforms import Form as NoCsrfForm
from wtforms import IntegerField, SelectField, StringField, \
    TextAreaField, FormField, RadioField
from wtforms.fields.core import UnboundField
from wtforms.validators import InputRequired, NumberRange, Optional

from cla_public.apps.checker.api import money_interval
from cla_public.apps.checker.constants import CATEGORIES, BENEFITS_CHOICES, \
    NON_INCOME_BENEFITS, YES, NO, DAY_CHOICES, CONTACT_SAFETY, \
    PASSPORTED_BENEFITS
from cla_public.apps.checker.fields import (
    AvailabilityCheckerField, DescriptionRadioField, MoneyIntervalField,
    MultiCheckboxField, YesNoField, PartnerYesNoField, MoneyField,
    PartnerMoneyIntervalField, PartnerMultiCheckboxField, PartnerMoneyField,
    PropertyList, money_interval_to_monthly,
    AdaptationsForm,
    PassKwargsToFormField)
from cla_public.apps.checker.form_config_parser import FormConfigParser
from cla_public.apps.checker.honeypot import Honeypot
from cla_public.apps.checker.utils import nass, passported, money_intervals_except, money_intervals
from cla_public.apps.checker.validators import AtLeastOne, IgnoreIf, \
    FieldValue, MoneyIntervalAmountRequired, NotRequired, FieldValueOrNone


log = logging.getLogger(__name__)


class ConfigFormMixin(object):
    def __init__(self, *args, **kwargs):
        config_path = kwargs.pop('config_path', None)

        super(ConfigFormMixin, self).__init__(*args, **kwargs)

        config = FormConfigParser(
            self.__class__.__name__, config_path=config_path)

        if config:
            # set config attributes on the field
            for field_name, field in self._fields.iteritems():
                field.__dict__.update(config.get(field_name, field))


class ProblemForm(ConfigFormMixin, Honeypot, Form):
    """Area of law choice"""

    categories = DescriptionRadioField(
        u'What do you need help with?',
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
        u'Do you have a partner?',
        description=(
            u"Your partner is your husband, wife, civil partner or someone "
            u"you live with as if you’re married"))
    in_dispute = YesNoField(
        u'If Yes, are you in a dispute with your partner?',
        description=(
            u"This means a dispute over money or property following a "
            u"separation"),
        validators=[
            IgnoreIf('have_partner', FieldValue(NO)),
            InputRequired(message=u'Please choose Yes or No')
        ])
    on_benefits = YesNoField(
        u'Do you receive any benefits (including Child Benefit)?',
        description=(
            u"Being on some benefits can help you qualify for legal aid"))
    have_children = YesNoField(
        u'Do you have any children aged 15 or under?',
        description=u"Don't include any children who don't live with you")
    num_children = IntegerField(
        u'If Yes, how many?',
        validators=[
            IgnoreIf('have_children', FieldValue(NO)),
            NumberRange(min=1)])
    have_dependants = YesNoField(
        u'Do you have any dependants aged 16 or over?',
        description=u"People who you live with and support financially")
    num_dependants = IntegerField(
        u'If Yes, how many?',
        validators=[
            IgnoreIf('have_dependants', FieldValue(NO)),
            NumberRange(min=1)])
    have_savings = YesNoField(
        u'Do you have any savings or investments?')
    have_valuables = YesNoField(
        u'Do you have any valuable items worth over £500 each?')
    own_property = YesNoField(
        u'Do you own any property?',
        description=u"For example, a house, static caravan or flat")
    is_employed = YesNoField(
        u'Are you employed?',
        description=(
            u"This means working as an employee - you may be both employed "
            u"and self-employed"))
    partner_is_employed = YesNoField(
        u'Is your partner employed?',
        description=(
            u"This means working as an employee - your partner may be both employed "
            u"and self-employed"),
        validators=[IgnoreIf('in_dispute', FieldValueOrNone(YES))])
    is_self_employed = YesNoField(
        u'Are you self-employed?',
        description=(
            u"This means working for yourself - you may be both employed "
            u"and self-employed"))
    partner_is_self_employed = YesNoField(
        u'Is your partner self-employed?',
        description=(
            u"This means working for yourself - your partner may be both employed "
            u"and self-employed"),
        validators=[IgnoreIf('in_dispute', FieldValueOrNone(YES))])
    aged_60_or_over = YesNoField(u'Are you aged 60 or over?')

    def api_payload(self):
        return {
            'dependants_young': self.num_children.data or 0,
            'dependants_old': self.num_dependants.data or 0,
            'is_you_or_your_partner_over_60': self.aged_60_or_over.data,
            'has_partner': self.have_partner.data,
            'you': {'income': {
                'self_employed': self.is_self_employed.data}}
        }


class YourBenefitsForm(ConfigFormMixin, Honeypot, Form):
    benefits = PartnerMultiCheckboxField(
        u'Are you or your partner on any of these benefits?',
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
        u'Is this property your main home?',
        description=(
            u"If you are separated and no longer live in the property you "
            u"own, please answer ‘no’"))
    other_shareholders = PartnerYesNoField(
        u'Does anyone else (other than you or your partner) own a share of the property?',
        description=u"Select 'Yes' if you share ownership with a friend, relative or ex-partner")
    property_value = MoneyField(
        u'How much is the property worth?',
        description=u"Use a property website or the Land Registry website",
        validators=[InputRequired(u'Please enter a valid amount'), NumberRange(min=0)])
    mortgage_remaining = MoneyField(
        u'How much is left to pay on the mortgage?',
        description=(
            u"Include the full amount owed, even if the property has "
            u"shared ownership"),
        validators=[InputRequired(u'Please enter 0 if you have no mortgage'), NumberRange(min=0)])
    mortgage_payments = MoneyField(
        u'How much are your monthly mortgage repayments?',
        validators=[IgnoreIf('mortgage_remaining', FieldValue(0)), NumberRange(min=0)])
    is_rented = YesNoField(u'Do you rent out any part of this property?')
    rent_amount = MoneyIntervalField(
        u'If Yes, how much rent do you receive?',
        choices=money_intervals_except('per_4week'),
        validators=[
            IgnoreIf('is_rented', FieldValue(NO)),
            MoneyIntervalAmountRequired()])
    in_dispute = YesNoField(
        u'Is your share of the property in dispute?',
        description=(
            u"For example, as part of the financial settlement of a divorce"))

    def api_payload(self):
        share = 100 if self.other_shareholders.data == NO else None
        return {
            'value': self.property_value.data,
            'mortgage_left': self.mortgage_remaining.data,
            'share': share,
            'disputed': self.in_dispute.data,
            'rent': self.rent_amount.data,
            'main': self.is_main_home.data
        }


def sum_money_intervals(first, second):
    first = money_interval_to_monthly(first)
    second = money_interval_to_monthly(second)
    return money_interval(
        first['per_interval_value'] + second['per_interval_value'],
        first['interval_period'])


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
        total_rent = reduce(sum_money_intervals, rents, money_interval(0))
        total_mortgage = sum(
            [p.mortgage_payments.data for p in self.properties if p.mortgage_payments.data is not None]
        )
        return {
            'property_set': properties,
            'you': {
                'income': {'other_income': total_rent},
                'deductions': {'mortgage': total_mortgage}
            }
        }


class SavingsForm(ConfigFormMixin, Honeypot, Form):
    savings = MoneyField(
        description=(
            u"The total amount of savings in cash, bank or building society"),
        validators=[InputRequired(
            message=u'Enter 0 if you have no savings'
        )])
    investments = MoneyField(
        description=u"This includes stocks, shares, bonds (but not property)",
        validators=[InputRequired(
            message=u'Enter 0 if you have no investments'
        )])
    valuables = PartnerMoneyField(
        u'Total value of items worth over £500 each')

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
        u'Child Benefit',
        description=u"The total amount you get for all your children",
        choices=money_intervals('', 'per_week', 'per_4week'),
        validators=[MoneyIntervalAmountRequired()])
    child_tax_credit = MoneyIntervalField(
        u'Child Tax Credit',
        description=u"The total amount you get for all your children",
        choices=money_intervals_except('per_month'),
        validators=[MoneyIntervalAmountRequired()])
    benefits = PartnerMultiCheckboxField(
        u'Do you or your partner get any of these benefits?',
        description=(
            u"These benefits don’t count as income. Please tick the ones you "
            u"receive."),
        choices=NON_INCOME_BENEFITS)
    other_benefits = PartnerYesNoField(
        u'Do you or your partner receive any other benefits not listed above? ',
        description=u'For example, Incapacity Benefit, \
            Contribution-based Jobseeker\'s Allowance')
    total_other_benefit = MoneyIntervalField(
        u'If Yes, total amount of benefits not listed above',
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
        u'Wages before tax',
        description=(
            u"This includes all your wages and any earnings from "
            u"self-employment"),
        validators=[MoneyIntervalAmountRequired()])
    income_tax = MoneyIntervalField(
        u'Income tax',
        description=(
            u"Tax paid directly out of your wages and any tax you pay on "
            u"self-employed earnings"),
        validators=[MoneyIntervalAmountRequired()])
    national_insurance = MoneyIntervalField(
        u'National Insurance contributions',
        description=(
            u"Check your payslip or your National Insurance statement if "
            u"you’re self-employed"),
        validators=[MoneyIntervalAmountRequired()])
    working_tax_credit = MoneyIntervalField(
        u'Working Tax Credit',
        description=u'Extra money for people who work and have a low income',
        validators=[MoneyIntervalAmountRequired()])
    maintenance = MoneyIntervalField(
        u'Maintenance received',
        description=u"Payments you get from an ex-partner",
        validators=[MoneyIntervalAmountRequired()])
    pension = MoneyIntervalField(
        u'Pension received',
        description=u"Payments you receive if you’re retired",
        validators=[MoneyIntervalAmountRequired()])
    other_income = MoneyIntervalField(
        u'Any other income',
        description=(
            u"For example, student grants, income from trust funds, "
            u"dividends"),
        validators=[MoneyIntervalAmountRequired()])

    def api_payload(self):
        tax_credits = self.working_tax_credit.data
        child_tax_credit = session.get(
            'TaxCreditsForm_child_tax_credit', money_interval(0))
        if not self.is_partner:
            tax_credits = sum_money_intervals(tax_credits, child_tax_credit)

        earnings = self.earnings.data
        self_employed_drawings = money_interval(0)
        # Switch all earnings to self employed drawings if only self employed
        if session.is_self_employed and not session.is_employed:
            earnings, self_employed_drawings = self_employed_drawings, earnings

        return {
            'income': {
                'earnings': earnings,
                'self_employment_drawings': self_employed_drawings,
                'tax_credits': tax_credits,
                'maintenance_received': self.maintenance.data,
                'pension': self.pension.data,
                'other_income': self.other_income.data
            },
            'deductions': {
                'income_tax': self.income_tax.data,
                'national_insurance': self.national_insurance.data,
            }
        }


class IncomeAndTaxForm(ConfigFormMixin, Honeypot, Form):
    your_income = FormField(IncomeFieldForm, label=u'Your personal income')

    def api_payload(self):
        partner_income = getattr(self, 'partner_income', None)
        if partner_income:
            partner_income = partner_income.form.api_payload()
        return {
            'you': self.your_income.form.api_payload(),
            'partner': partner_income
        }


def income_form(*args, **kwargs):
    """Dynamically add partner subform if user has a partner"""

    class IncomeForm(IncomeAndTaxForm):
        pass

    if session.has_partner:
        IncomeForm.partner_income = PassKwargsToFormField(
            IncomeFieldForm,
            form_kwargs={'is_partner': True},
            label=u'Your partner‘s income')

    return IncomeForm(*args, **kwargs)


class OutgoingsForm(ConfigFormMixin, Honeypot, Form):
    rent = PartnerMoneyIntervalField(
        u'Rent',
        description=u"Money you and your partner pay your landlord",
        choices=money_intervals_except('per_4week'),
        validators=[MoneyIntervalAmountRequired()])
    maintenance = PartnerMoneyIntervalField(
        u'Maintenance',
        description=(
            u"Money you and/or your partner pay to an ex-partner for their "
            u"living costs"),
        validators=[MoneyIntervalAmountRequired()])
    income_contribution = PartnerMoneyField(
        u'Monthly Income Contribution Order',
        description=(
            u"Money you and/or your partner pay per month towards your criminal legal "
            u"aid"))
    childcare = PartnerMoneyIntervalField(
        u'Childcare',
        description=(
            u"Money you and your partner pay for your child to be looked "
            u"after while you work or study"),
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


class ApplicationForm(Honeypot, Form):
    full_name = StringField(
        u'Full name',
        validators=[InputRequired()])
    contact_number = StringField(
        u'Contact phone number',
        validators=[InputRequired()])
    safe_to_contact = RadioField(
        u'Is it safe for us to leave a message on this number?',
        choices=CONTACT_SAFETY,
        validators=[InputRequired(message=u'Please choose Yes or No')],
    )
    post_code = StringField(u'Postcode')
    address = TextAreaField(u'Address')
    extra_notes = TextAreaField(
        u'Help the operator to understand your situation',
        description=(
            u"If you’d like to tell us more about your problem, please do so in the "
            u"box below. The Civil Legal Advice operator will read this before "
            u"they call you."),
        validators=[Optional()])
    adaptations = FormField(
        AdaptationsForm,
        u'Do you have any special communication needs?')

    time = AvailabilityCheckerField(u'Select a time for us to call you')

    def api_payload(self):
        time = self.time.scheduled_time().replace(tzinfo=pytz.utc)
        return {
            'personal_details': {
                'full_name': self.full_name.data,
                'postcode': self.post_code.data,
                'mobile_phone': self.contact_number.data,
                'street': self.address.data,
                'safe_to_contact': self.safe_to_contact.data
            },
            'adaptation_details': {
                'bsl_webcam': self.adaptations.bsl_webcam.data,
                'minicom': self.adaptations.minicom.data,
                'text_relay': self.adaptations.text_relay.data,
                'language':
                    self.adaptations.welsh.data and 'WELSH'
                    or self.adaptations.other_language.data,
                'notes': self.adaptations.other_adaptation.data
                    if self.adaptations.is_other_adaptation.data else ''
            },
            'requires_action_at': time.isoformat(),
        }
