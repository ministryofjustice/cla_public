# -*- coding: utf-8 -*-
"Custom form fields"

import logging
import re

from flask import session

from flask.ext.babel import lazy_gettext as _
from wtforms import Form as NoCsrfForm
from wtforms import FormField, IntegerField, RadioField, \
    SelectField, SelectMultipleField, widgets, FieldList
from wtforms.validators import Optional, InputRequired

from cla_common.money_interval.models import MoneyInterval
from cla_public.apps.base.forms import BabelTranslationsFormMixin
from cla_public.apps.checker.constants import MONEY_INTERVALS, NO, YES
from cla_public.apps.checker.validators import ValidMoneyInterval


log = logging.getLogger(__name__)


def coerce_unicode_if_value(value):
    return unicode(value) if value is not None else None


class PartnerMixin(object):

    def __init__(self, *args, **kwargs):
        partner_label = kwargs.pop('partner_label', kwargs.get('label'))
        partner_description = kwargs.pop(
            'partner_description', kwargs.get('description'))
        if session.has_partner:
            kwargs['label'] = partner_label
            kwargs['description'] = partner_description
        super(PartnerMixin, self).__init__(*args, **kwargs)


class DescriptionRadioField(RadioField):
    """RadioField with a description for each radio button, not just for the
    group.

    The choices kwargs field takes a list of triples.

    Format:

    choices=[(name, label, description), ...]
    """

    def __init__(self, *args, **kwargs):
        self.options_attributes = []
        self.field_names = []
        self.descriptions = []
        choices = []
        for name, label, description in kwargs.get('choices', []):
            self.field_names.append(name)
            self.descriptions.append(description)
            choices.append((name, label))
        if choices:
            kwargs['choices'] = choices
        super(DescriptionRadioField, self).__init__(*args, **kwargs)

    def __iter__(self):
        options = super(DescriptionRadioField, self).__iter__()
        for index, option in enumerate(options):
            option.description = self.descriptions[index]
            option.field_name = self.field_names[index]

            try:
                option_attributes = self.options_attributes[index]
                option.__dict__.update(option_attributes)
            except IndexError:
                pass

            yield option

    def add_options_attributes(self, options_attributes):
        self.options_attributes = options_attributes


class YesNoField(RadioField):
    """Yes/No radio button field"""

    def __init__(self, label=None, validators=None, yes_text=_('Yes'),
                 no_text=_('No'), **kwargs):
        choices = [(YES, yes_text), (NO, no_text)]
        if validators is None:
            validators = [
                InputRequired(message=self.gettext(u'Please choose Yes or No'))]
        super(YesNoField, self).__init__(
            label=label, validators=validators, coerce=coerce_unicode_if_value,
            choices=choices, **kwargs)


def set_zero_values(form):
    """Set values on a form to zero"""
    def set_zero(field):
        if hasattr(field, 'set_zero'):
            field.set_zero()
    map(set_zero, form._fields.itervalues())
    return form


class SetZeroIntegerField(IntegerField):
    def set_zero(self):
        self.data = 0


class SetZeroFormField(FormField):
    def set_zero(self):
        set_zero_values(self.form)


class MoneyField(SetZeroIntegerField):

    def __init__(self, label=None, validators=None, min_val=0, max_val=None,
                 **kwargs):
        super(MoneyField, self).__init__(label, validators, **kwargs)
        self.min_val = min_val
        self.max_val = max_val

    def process_formdata(self, valuelist):
        if valuelist:
            pounds, _, pence = valuelist[0].strip().partition('.')
            pounds = re.sub(r'[\s,]+', '', pounds)

            if pence:
                if len(pence) > 2:
                    self.data = None
                    raise ValueError(self.gettext(u'Not a valid amount'))

                if len(pence) == 1:
                    pence = '{0}0'.format(pence)

            try:
                self.data = int(pounds) * 100
                if pence:
                    self.data += int(pence)
            except ValueError:
                self.data = None
                raise ValueError(self.gettext(u'Not a valid amount'))

            if self.min_val is not None and self.data < self.min_val:
                self.data = None
                raise ValueError(self.gettext(
                    u'This amount must be more than £{:.0f}'.format(
                        self.min_val / 100.0)))

            if self.max_val is not None and self.data > self.max_val:
                self.data = None
                raise ValueError(self.gettext(
                    u'This amount must be less than £{:.0f}'.format(
                        self.max_val / 100.0)))

    def process_data(self, value):
        self.data = value
        if value:
            pence = value % 100
            pounds = value / 100
            self.data = '{0}.{1:02}'.format(pounds, pence)


class MoneyIntervalForm(NoCsrfForm, BabelTranslationsFormMixin):
    """Money amount and interval subform"""
    per_interval_value = MoneyField(validators=[Optional()])
    interval_period = SelectField(
        '',
        choices=MONEY_INTERVALS,
        coerce=coerce_unicode_if_value)

    def __init__(self, *args, **kwargs):
        # Enable choices to be passed through
        choices = kwargs.pop('choices', None)
        super(MoneyIntervalForm, self).__init__(*args, **kwargs)
        if choices:
            self.interval_period.choices = choices

    @property
    def data(self):
        data = super(MoneyIntervalForm, self).data
        if data['per_interval_value'] is 0 and not data['interval_period']:
            data['interval_period'] = MONEY_INTERVALS[1][0]
        return data


def money_interval_to_monthly(data):
    amount = data['per_interval_value']
    interval = data['interval_period']

    if amount is None or interval == '':
        return {
            'per_interval_value': 0,
            'interval_period': 'per_month'
        }

    if interval == 'per_month':
        return data

    multiplier = MoneyInterval._intervals_dict[interval]['multiply_factor']

    return {
        'per_interval_value': amount * multiplier,
        'interval_period': 'per_month'
    }


class PassKwargsToFormField(SetZeroFormField):

    def __init__(self, *args, **kwargs):
        form_kwargs = kwargs.pop('form_kwargs', {})

        super(PassKwargsToFormField, self).__init__(*args, **kwargs)
        self._form_class = self.form_class

        def form_class_proxy(*f_args, **f_kwargs):
            f_kwargs.update(form_kwargs)
            return self._form_class(*f_args, **f_kwargs)

        self.form_class = form_class_proxy


class MoneyIntervalField(PassKwargsToFormField):
    """Convenience class for FormField(MoneyIntervalForm)"""

    def __init__(self, *args, **kwargs):
        self._errors = []
        self.validators = []
        if 'validators' in kwargs:
            self.validators.extend(kwargs['validators'])
            del kwargs['validators']
        self.validators.append(ValidMoneyInterval())

        # Enable kwarg choices to be passed through to interval field
        choices = kwargs.pop('choices', None)

        super(MoneyIntervalField, self).__init__(
            MoneyIntervalForm,
            form_kwargs={'choices': choices},
            *args, **kwargs)

    def as_monthly(self):
        return money_interval_to_monthly(self.data)

    def validate(self, form, extra_validators=None):
        self._run_validation_chain(form, self.validators)
        return len(self.errors) == 0

    @property
    def errors(self):
        return self._errors

    @errors.setter
    def errors(self, _errors):
        self._errors = _errors

    def set_zero(self):
        self.form.per_interval_value.data = 0
        self.form.interval_period.data = 'per_month'


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class PropertyList(FieldList):
    def remove(self, index):
        del self.entries[index]
        self.last_index -= 1

    def validate(self, form, extra_validators=tuple()):
        super(PropertyList, self).validate(form, extra_validators)

        main_properties = filter(
            lambda x: x.is_main_home.data == YES,
            self.entries)

        if len(main_properties) > 1:
            message = self.gettext('You can only have 1 main Property')
            map(
                lambda x: x.is_main_home.errors.append(message),
                main_properties)
            self.errors.append(message)

        return len(self.errors) == 0

    def set_zero(self):
        self.entries = []


class PartnerMoneyIntervalField(PartnerMixin, MoneyIntervalField):
    pass


class PartnerIntegerField(PartnerMixin, SetZeroIntegerField):
    pass


class PartnerYesNoField(PartnerMixin, YesNoField):
    pass


class PartnerMultiCheckboxField(PartnerMixin, MultiCheckboxField):
    pass


class PartnerMoneyField(PartnerMixin, MoneyField):
    pass
