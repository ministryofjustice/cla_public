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
    categories = DesciptionRadioField(
        u'What do you need help with?',
        choices=CATEGORIES,
        coerce=unicode,
        validators=[InputRequired()])


class AboutYouForm(Form):
    have_partner = YesNoField(u'Do you have a partner?')
    in_dispute = YesNoField(u'Are you in a dispute with your partner?')
    on_benefits = YesNoField(u'Are you on any benefits?')
    have_children = YesNoField(u'Do you have any children aged 15 or under?')
    num_children = IntegerField(u'How many?')
    have_dependants = YesNoField(u'Do you have any dependants aged 16 or over?')
    num_dependants = IntegerField(u'How many?')
    have_savings = YesNoField(u'Do you have any savings, investments or any valuable items?')
    own_property = YesNoField(u'Do you own any property?')
    employed = YesNoField(u'Are you employed?')
    self_employed = YesNoField(u'Are you self-employed?')
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
