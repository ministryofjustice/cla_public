# -*- coding: utf-8 -*-
"Custom form fields"

from wtforms import Form as NoCsrfForm
from wtforms import FormField, IntegerField, RadioField, SelectField, \
    SelectMultipleField, widgets
from wtforms.compat import text_type

from cla_public.apps.checker.constants import MONEY_INTERVALS


class DescriptionRadioField(RadioField):
    """RadioField with a description for each radio button, not just for the
    group.

    The choices kwargs field takes a list of triples.

    Format:

    choices=[(name, label, description), ...]
    """

    def __init__(self, *args, **kwargs):
        self.descriptions = []
        choices = []
        for name, label, description in kwargs.get('choices', []):
            self.descriptions.append(description)
            choices.append((name, label))
        if choices:
            kwargs['choices'] = choices
        super(DescriptionRadioField, self).__init__(*args, **kwargs)

    def __iter__(self):
        options = super(DescriptionRadioField, self).__iter__()
        for index, option in enumerate(options):
            option.description = self.descriptions[index]
            yield option


class YesNoField(RadioField):
    """Yes/No radio button field"""

    def __init__(self, label=None, validators=None, **kwargs):
        choices = [('1', 'Yes'), ('0', 'No')]
        super(YesNoField, self).__init__(
            label=label, validators=validators, coerce=text_type,
            choices=choices, **kwargs)


class MoneyIntervalForm(NoCsrfForm):
    """Money amount and interval subform"""
    amount = IntegerField()
    interval = SelectField('', choices=MONEY_INTERVALS)


class MoneyIntervalField(FormField):
    """Convenience class for FormField(MoneyIntervalForm)"""

    widget = widgets.ListWidget()

    def __init__(self, **kwargs):
        super(MoneyIntervalField, self).__init__(MoneyIntervalForm, **kwargs)


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()
