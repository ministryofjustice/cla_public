# -*- coding: utf-8 -*-
"Custom form fields"

import logging
import re
import datetime

from flask import session
import pytz
from wtforms import Form as NoCsrfForm, TextAreaField
from wtforms import FormField, BooleanField, IntegerField, Label, RadioField, \
    SelectField, SelectMultipleField, widgets, FieldList, StringField
from wtforms.compat import text_type
from wtforms.validators import Optional, StopValidation, InputRequired

from cla_common.constants import ADAPTATION_LANGUAGES
from cla_common.money_interval.models import MoneyInterval
from cla_public.apps.checker.constants import MONEY_INTERVALS, NO, YES, \
    DAY_CHOICES, DAY_TODAY, DAY_TOMORROW, DAY_SPECIFIC
from cla_public.apps.checker.validators import ValidMoneyInterval, IgnoreIf, \
    FieldValue, FieldValueNot, AvailableSlot
from cla_public.libs.call_centre_availability import day_choice, \
    available_days, time_choice, today_slots, \
    tomorrow_slots, time_slots, available


log = logging.getLogger(__name__)
partner_regex = re.compile(r'(and/or|and|or) your partner')


LANG_CHOICES = filter(
    lambda x: x[0] not in ('ENGLISH', 'WELSH'),
    [('', '-- Choose a language --')] + ADAPTATION_LANGUAGES)


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

    def __init__(self, label=None, validators=None, **kwargs):
        choices = [(YES, 'Yes'), (NO, 'No')]
        if validators is None:
            validators = [InputRequired(message=u'Please choose Yes or No')]
        super(YesNoField, self).__init__(
            label=label, validators=validators, coerce=text_type,
            choices=choices, **kwargs)


class MoneyField(IntegerField):

    def __init__(self, label=None, validators=None, min_val=0, max_val=None,
                 **kwargs):
        super(MoneyField, self).__init__(label, validators, **kwargs)
        self.min_val = min_val
        self.max_val = max_val

    def process_formdata(self, valuelist):
        if valuelist:
            pounds, _, pence = valuelist[0].partition('.')
            pounds = re.sub(r'[\s,]+', '', pounds)

            if pence and len(pence) != 2:
                self.data = None
                raise ValueError(self.gettext(u'Not a valid amount'))

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


class MoneyIntervalForm(NoCsrfForm):
    """Money amount and interval subform"""
    per_interval_value = MoneyField(validators=[Optional()])
    interval_period = SelectField('', choices=MONEY_INTERVALS)

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


class MoneyIntervalField(FormField):
    """Convenience class for FormField(MoneyIntervalForm)"""

    def __init__(self, *args, **kwargs):
        self._errors = []
        self.validators = []
        if 'validators' in kwargs:
            self.validators.extend(kwargs['validators'])
            del kwargs['validators']
        self.validators.append(ValidMoneyInterval())

        # Enable kwarg choices to be passed through to interval field
        self.choices = kwargs.pop('choices', None)

        super(MoneyIntervalField, self).__init__(
            MoneyIntervalForm, *args, **kwargs)

        # If choices passed through then proxy the self.form_class creator
        # and pass through the choices when the cinstance is created
        if self.choices:
            self._form_class = self.form_class

            def form_class_proxy(*args, **kwargs):
                return self._form_class(choices=self.choices, *args, **kwargs)

            self.form_class = form_class_proxy

    def as_monthly(self):
        return money_interval_to_monthly(self.data)

    def validate(self, form, extra_validators=None):
        stop_validation = self._run_validation_chain(form, self.validators)
        return len(self.errors) == 0

    @property
    def errors(self):
        return self._errors

    @errors.setter
    def errors(self, _errors):
        self._errors = _errors


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


class PartnerMoneyIntervalField(MoneyIntervalField, PartnerMixin):
    pass


class PartnerIntegerField(IntegerField, PartnerMixin):
    pass


class PartnerYesNoField(YesNoField, PartnerMixin):
    pass


class PartnerMultiCheckboxField(MultiCheckboxField, PartnerMixin):
    pass


class AdaptationsForm(NoCsrfForm):
    bsl_webcam = BooleanField(u'BSL - Webcam')
    minicom = BooleanField(u'Minicom')
    text_relay = BooleanField(u'Text Relay')
    welsh = BooleanField(u'Welsh')
    is_other_language = BooleanField(u'Other language')
    other_language = SelectField(
        u'Language required:',
        choices=(LANG_CHOICES))
    is_other_adaptation = BooleanField(u'Any other communication needs')
    other_adaptation = TextAreaField(
        u'Other communication needs',
        description=u'Please tell us what you need in the box below')


class PartnerMoneyField(MoneyField, PartnerMixin):
    pass


class FormattedChoiceField(object):

    def process_data(self, value):
        self.data = value
        if value:
            self.data = self._format(value)

    def pre_validate(self, form):
        choice_values = (v for v, _ in self.choices)
        if self._format(self.data) not in choice_values:
            raise ValueError(self.gettext('Not a valid choice'))


class DayChoiceField(FormattedChoiceField, SelectField):

    def __init__(self, num_days=6, *args, **kwargs):
        super(DayChoiceField, self).__init__(*args, **kwargs)
        self.choices = map(day_choice, available_days(num_days))

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                year = int(valuelist[0][:4])
                month = int(valuelist[0][4:6])
                day = int(valuelist[0][6:])
                self.data = datetime.date(year, month, day)
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid date'))

    def _format(self, value):
        return '{:%Y%m%d}'.format(value)


class TimeChoiceField(FormattedChoiceField, SelectField):

    def __init__(self, choices_callback=None, validators=None, **kwargs):
        super(TimeChoiceField, self).__init__(validators=validators, **kwargs)
        self.choices = map(time_choice, choices_callback())

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                hour = int(valuelist[0][:2])
                minute = int(valuelist[0][2:])
                self.data = datetime.time(hour, minute)
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid time'))

    def _format(self, value):
        return '{:%H%M}'.format(value)


class AvailabilityCheckerForm(NoCsrfForm):
    specific_day = RadioField(
        label=u'Arrange a callback time',
        choices=DAY_CHOICES,
        default=DAY_TODAY)

    # choices must be set dynamically as cache is not available at runtime
    time_today = TimeChoiceField(
        today_slots,
        validators=[
            IgnoreIf('specific_day', FieldValueNot(DAY_TODAY)),
            AvailableSlot(DAY_TODAY)],
        id='id_time_today')
    time_tomorrow = TimeChoiceField(
        tomorrow_slots,
        validators=[
            IgnoreIf('specific_day', FieldValueNot(DAY_TOMORROW)),
            AvailableSlot(DAY_TOMORROW)],
        id='id_time_tomorrow')
    day = DayChoiceField(
        validators=[
            IgnoreIf('specific_day', FieldValueNot(DAY_SPECIFIC)),
            InputRequired()],
        id='id_day')
    time_in_day = TimeChoiceField(
        time_slots,
        validators=[
            IgnoreIf('specific_day', FieldValueNot(DAY_SPECIFIC)),
            AvailableSlot(DAY_SPECIFIC)],
        id='id_time_in_day')

    def __init__(self, *args, **kwargs):
        kwargs['prefix'] = ''
        super(AvailabilityCheckerForm, self).__init__(*args, **kwargs)
        if not self.time_today.choices:
            self.specific_day.data = DAY_TOMORROW
        if not self.time_tomorrow.choices and self.specific_day.data == DAY_TOMORROW:
            self.specific_day.data = DAY_SPECIFIC

    def scheduled_time(self, today=None):
        date = today or datetime.date.today()
        time = None

        if self.specific_day.data == DAY_TODAY:
            time = self.time_today.data

        if self.specific_day.data == DAY_TOMORROW:
            date += datetime.timedelta(days=1)
            time = self.time_tomorrow.data

        if self.specific_day.data == DAY_SPECIFIC:
            date = self.day.data
            time = self.time_in_day.data

        if date and time:
            return datetime.datetime.combine(date, time)

        return None


class AvailabilityCheckerField(FormField):
    """Convenience class for FormField(AvailabilityCheckerForm"""

    def __init__(self, *args, **kwargs):
        super(AvailabilityCheckerField, self).__init__(
            AvailabilityCheckerForm, *args, **kwargs)

    def scheduled_time(self):
        return self.form.scheduled_time()
