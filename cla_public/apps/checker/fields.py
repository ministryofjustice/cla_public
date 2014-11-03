# -*- coding: utf-8 -*-
"Custom form fields"

from flask_wtf import Form
from wtforms import FormField, IntegerField, RadioField, SelectField, \
    SelectMultipleField, widgets
from wtforms.compat import text_type
from wtforms.validators import InputRequired

from cla_public.apps.checker.constants import MONEY_INTERVALS


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

    def __init__(self, label=None, validators=None, **kwargs):
        choices = [('1', 'Yes'), ('0', 'No')]
        super(YesNoField, self).__init__(
            label=label, validators=validators, coerce=text_type,
            choices=choices, **kwargs)


class MoneyIntervalForm(Form):
    """Money amount and interval subform"""
    amount = IntegerField()
    interval = SelectField('', choices=MONEY_INTERVALS)


class MoneyIntervalField(FormField):
    """Convenience class for FormField(MoneyIntervalForm)"""

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
