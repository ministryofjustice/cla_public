# -*- coding: utf-8 -*-
"Checker forms"

from flask_wtf import Form
from wtforms import IntegerField, StringField, TextAreaField
from wtforms.validators import InputRequired, ValidationError, Optional

from cla_public.apps.checker.constants import CATEGORIES, BENEFITS_CHOICES, \
    NON_INCOME_BENEFITS
from cla_public.apps.checker.fields import DescriptionRadioField, \
    MoneyIntervalField, MultiCheckboxField, YesNoField


class ProblemForm(Form):
    """Area of law choice"""
    categories = DescriptionRadioField(
        u'What do you need help with?',
        choices=CATEGORIES,
        coerce=unicode,
        validators=[InputRequired()])


class AboutYouForm(Form):
    have_partner = YesNoField(u'Do you have a partner?',
        description=u"Your partner is your husband, wife, civil partner or someone you live with as if you’re married")
    in_dispute = YesNoField(u'Are you in a dispute with your partner?',
        description=u"This means a dispute over money or property following a separation")
    on_benefits = YesNoField(u'Are you on any benefits?',
        description=u"Being on some benefits can help you qualify for legal aid")
    have_children = YesNoField(u'Do you have any children aged 15 or under?',
        description=u"Don’t include any children who don’t live with you")
    num_children = IntegerField(u'How many?')
    have_dependants = YesNoField(u'Do you have any dependants aged 16 or over?',
        description=u"People who you live with and support financially")
    num_dependants = IntegerField(u'How many?')
    have_savings = YesNoField(u'Do you have any savings, investments or any valuable items?',
        description=u"Valuable items are worth over £500 each with some exceptions")
    own_property = YesNoField(u'Do you own any property?',
        description=u"For example, a house, flat or static caravan")
    is_employed = YesNoField(u'Are you employed?',
        description=u"This means working as an employee - you may be both employed and self-employed")
    is_self_employed = YesNoField(u'Are you self-employed?',
        description=u"This means working for yourself - you may be both employed and self-employed")
    aged_60_or_over = YesNoField(u'Are you aged 60 or over?')


class AtLeastOne(object):
    """
    Valid if at least one option is checked.

    :param message:
        Error message to raise in case of a validation error.
    """
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        if len(field.data) < 1:
            message = self.message
            if message is None:
                message = field.gettext('Must select at least one option.')
            raise ValidationError(message)


class YourBenefitsForm(Form):
    benefits = MultiCheckboxField(choices=BENEFITS_CHOICES,
            validators=[AtLeastOne()])


class PropertyForm(Form):
    is_main_home = YesNoField(u'Is this property your main home?',
        description=u"If you are separated and no longer live in the property you own, please answer ‘no’")
    other_shareholders = YesNoField(u'Does anyone else own a share of the property?',
        description=u"Other than you and your partner")
    property_value = IntegerField(u'How much is the property worth?',
        description=u"Use your own estimate")
    mortgage_remaining = IntegerField(u'How much is left to pay on the mortgage?',
        description=u"Include the full amount you owe, even if the property has shared ownership")
    mortgage_payments = IntegerField(u'How much are your monthly mortgage repayments?')
    is_rented = YesNoField(u'Does anyone pay you rent for this property?')
    rent_amount = IntegerField(u'How much rent do they pay you?')
    in_dispute = YesNoField(u'Is your share of the property in dispute?',
        description=u"For example, as part of the financial settlement of a divorce")


class SavingsForm(Form):
    savings = IntegerField(description=u"The total amount of savings in cash, bank or building society")
    investments = IntegerField(description=u"This includes stocks, shares, bonds (but not property)")
    valuables = IntegerField(u'Valuable items you and your partner own worth over £500 each',
        description=u"Total value of any items you own with some exceptions")


class TaxCreditsForm(Form):
    child_benefit = IntegerField(u'Child Benefit',
        description=u"The total amount you get for all your children")
    child_tax_credit = IntegerField(u'Child Tax Credit',
        description=u"The total amount you get for all your children")
    benefits = MultiCheckboxField(u'Do you or your partner get any of these benefits?',
        description=u"These benefits don’t count as income. Please tick the ones you receive.",
        choices=NON_INCOME_BENEFITS)
    other_benefits = YesNoField('Do you or your partner receive any other benefits not listed above?')
    total_other_benefit = MoneyIntervalField('Total amount of benefits not listed above')


class IncomeAndTaxForm(Form):
    earnings = MoneyIntervalField(u'Wages before tax',
        description=u"This includes all your wages and any earnings from self-employment")
    income_tax = MoneyIntervalField(u'Income tax',
        description=u"Tax paid directly out of your wages and any tax you pay on self-employed earnings")
    national_insurance = MoneyIntervalField(u'National Insurance contributions',
        description=u"Check your payslip or your National Insurance statement if you’re self-employed")
    working_tax_credit = MoneyIntervalField(u'Working Tax Credit')
    maintenance = MoneyIntervalField(u'Maintenance received',
        description=u"Payments you get from an ex-partner")
    pension = MoneyIntervalField(u'Pension received',
        description=u"Payments you receive if you’re retired")
    other_income = MoneyIntervalField(u'Any other income',
        description=u"For example, student grants, income from trust funds, dividends")


class OutgoingsForm(Form):
    rent = MoneyIntervalField(u'Rent',
        description=u"Money you and your partner pay your landlord")
    maintenance = MoneyIntervalField(u'Maintenance',
        description=u"Money you and/or your partner pay to an ex-partner for their living costs")
    income_contribution = MoneyIntervalField(u'Income Contribution Order',
        description=u"Money you and/or your partner pay towards your criminal legal aid")
    childcare = MoneyIntervalField(u'Childcare',
        description=u"Money you and your partner pay for your child to be looked after while you work or study")


class ApplicationForm(Form):
    title = StringField(u'Title', description=u"Mr, Mrs, Ms", validators=[InputRequired()])
    full_name = StringField(u'Full name', validators=[InputRequired()])
    contact_number = StringField(u'Contact phone number', validators=[InputRequired()])
    post_code = StringField(u'Postcode')
    address = TextAreaField(u'Address')
    extra_notes = TextAreaField(u'Help the operator to understand your situation',
        description=u"In your own words, please tell us exactly what your problem is about. The Civil Legal Advice operator will read this before they call you.")
