# -*- coding: utf-8 -*-
"Checker forms"

from flask_wtf import Form
from wtforms import IntegerField, RadioField
from wtforms.validators import InputRequired

from cla_public.apps.checker.constants import CATEGORIES, RESULT_OPTIONS, \
    BENEFITS_CHOICES
from cla_public.apps.checker.fields import HelpTextRadioField, \
    MoneyIntervalField, MultiCheckboxField, YesNoField


class ProblemForm(Form):
    """Area of law choice"""
    categories = HelpTextRadioField(
        u'What do you need help with?',
        choices=CATEGORIES,
        coerce=unicode,
        validators=[InputRequired()])


class AboutYouForm(Form):
    have_partner = YesNoField()
    in_dispute = YesNoField()
    on_benefits = YesNoField()
    have_children = YesNoField()
    num_children = IntegerField()
    have_dependants = YesNoField()
    num_dependants = IntegerField()
    have_savings = YesNoField()
    own_property = YesNoField()
    employed = YesNoField()
    self_employed = YesNoField()
    aged_60_or_over = YesNoField()


class YourBenefitsForm(Form):
    benefits = MultiCheckboxField(choices=BENEFITS_CHOICES)


class ProceedForm(Form):
    proceed = YesNoField()


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


class ResultForm(Form):
    result = RadioField(
        choices=RESULT_OPTIONS,
        validators=[InputRequired(u'Not a valid choice')])
