# -*- coding: utf-8 -*-
"Checker forms"

from flask_wtf import Form
from wtforms import FormField, IntegerField, RadioField, SelectField, \
    SelectMultipleField, widgets
from wtforms.validators import InputRequired

from .constants import CATEGORIES, RESULT_OPTIONS, BENEFITS_CHOICES, \
    MONEY_INTERVALS


class HelpTextRadioField(RadioField):
    """RadioField that also stores an field for inline help text

    The choices kwargs field takes a list of triples.

    Format:

    choices=[(name, label, helptext), ...]
    """

    def __init__(self, *args, **kwargs):
        self.helptext = []
        choices = []
        for name, label, helptext in kwargs.get('choices', []):
            self.helptext.append(helptext)
            choices.append((name, label))
        if choices:
            kwargs['choices'] = choices
        super(HelpTextRadioField, self).__init__(*args, **kwargs)

    def __iter__(self):
        options = super(HelpTextRadioField, self).__iter__()
        for index, option in enumerate(options):
            option.helptext = self.helptext[index]
            yield option


class YesNoField(RadioField):
    """Yes/No radio button field"""

    def __init__(self, *args, **kwargs):
        kwargs['choices'] = [('1', 'Yes'), ('0', 'No')]
        kwargs['validators'] = [InputRequired()]
        super(YesNoField, self).__init__(self, *args, **kwargs)


class MoneyIntervalForm(Form):
    """Money amount and interval subform"""
    amount = IntegerField()
    interval = SelectField('', choices=MONEY_INTERVALS)


class MoneyIntervalField(FormField):
    """Convenience class for FormField(MoneyIntervalForm)"""

    def __init__(self, *args, **kwargs):
        super(MoneyIntervalField, self).__init__(MoneyIntervalForm, **kwargs)


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


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
    benefits = RadioField(choices=BENEFITS_CHOICES)


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
