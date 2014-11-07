# -*- coding: utf-8 -*-
"Custom form fields"

import re

from flask import session
from wtforms import Form as NoCsrfForm
from wtforms import FormField, IntegerField, Label, RadioField, SelectField, \
    SelectMultipleField, widgets
from wtforms.compat import text_type

from cla_public.apps.checker.constants import MONEY_INTERVALS, NO, YES


partner_regex = re.compile(r'(and\/or|and|or) your partner')


class DynamicPartnerLabel(Label):

    def __call__(self, text=None, **kwargs):
        if not text:
            text = self.text
        if not session.has_partner and 'partner' in text:
            text = re.sub(partner_regex, '', text)
        return super(DynamicPartnerLabel, self).__call__(text, **kwargs)


class PartnerMixin(object):

    @property
    def label(self):
        if not hasattr(self, '_label'):
            return None
        return self._label

    @label.setter
    def label(self, value):
        self._label = DynamicPartnerLabel(self.id, value.text)

    @property
    def description(self):
        if not hasattr(self, '_description'):
            return None
        desc = self._description
        if not session.has_partner and 'partner' in self._description:
            desc = re.sub(partner_regex, '', desc)
        return desc

    @description.setter
    def description(self, value):
        self._description = value


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
        choices = [(YES, 'Yes'), (NO, 'No')]
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

    def __init__(self, *args, **kwargs):
        super(MoneyIntervalField, self).__init__(
            MoneyIntervalForm, *args, **kwargs)


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class PartnerMoneyIntervalField(MoneyIntervalField, PartnerMixin):
    pass


class PartnerIntegerField(IntegerField, PartnerMixin):
    pass


class PartnerYesNoField(YesNoField, PartnerMixin):
    pass


class PartnerMultiCheckboxField(MultiCheckboxField, PartnerMixin):
    pass
