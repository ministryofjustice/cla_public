# -*- coding: utf-8 -*-
"Checker forms"

from flask_wtf import Form
from wtforms import IntegerField
from wtforms.validators import InputRequired

from cla_public.apps.checker.constants import CATEGORIES, BENEFITS_CHOICES
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


class YourBenefitsForm(Form):
    benefits = MultiCheckboxField(choices=BENEFITS_CHOICES)


class PropertyForm(Form):
    main_home = YesNoField()
    other_shareholders = YesNoField()
    property_value = IntegerField()
    mortgage_remaining = IntegerField()
    mortgage_payments = IntegerField()
    rented = YesNoField()
    rent_amount = IntegerField()
    in_dispute = YesNoField()


class SavingsForm(Form):
    savings = IntegerField()
    investments = IntegerField()
    valuables = IntegerField()


class TaxCreditsForm(Form):
    child_benefit = IntegerField()
    child_tax_credit = IntegerField()
    benefits = MultiCheckboxField()
    other_benefits = YesNoField()
    total_other_benefit = IntegerField()


class IncomeAndTaxForm(Form):
    earnings = MoneyIntervalField()
    incometax = MoneyIntervalField()
    national_insurance = MoneyIntervalField()
    working_tax_credit = MoneyIntervalField()
    maintenance = MoneyIntervalField()
    pension = MoneyIntervalField()
    other_income = MoneyIntervalField()


class OutgoingsForm(Form):
    rent = MoneyIntervalField()
    maintenance = MoneyIntervalField()
    income_contribution = MoneyIntervalField()
    childcare = MoneyIntervalField()
