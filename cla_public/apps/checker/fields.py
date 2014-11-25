# -*- coding: utf-8 -*-
"Custom form fields"

import logging
import re
import datetime

from flask import session
import pytz
from wtforms import Form as NoCsrfForm, TextAreaField
from wtforms import FormField, BooleanField, IntegerField, Label, RadioField, \
    SelectField, SelectMultipleField, widgets, FieldList
from wtforms.compat import text_type
from wtforms.validators import Optional, StopValidation, InputRequired

from cla_common.constants import ADAPTATION_LANGUAGES
from cla_common.money_interval.models import MoneyInterval
from cla_public.apps.checker.constants import MONEY_INTERVALS, NO, YES, \
    DAY_CHOICES
from cla_public.apps.checker.validators import ValidMoneyInterval
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
        self.field_names = []
        self.more_infos = []
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
                option.more_info = self.more_infos[index]
            except IndexError:
                option.more_info = None
            yield option

    def add_more_infos(self, more_infos):
        self.more_infos = more_infos


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
    amount = MoneyField(validators=[Optional()])
    interval = SelectField('', choices=MONEY_INTERVALS)


def money_interval_to_monthly(data):
    amount = data['amount']
    interval = data['interval']

    if amount is None or interval == '':
        return {
            'amount': 0,
            'interval': 'per_month'
        }

    if interval == 'per_month':
        return data

    multiplier = MoneyInterval._intervals_dict[interval]['multiply_factor']

    return {
        'amount': amount * multiplier,
        'interval': 'per_month'
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

        super(MoneyIntervalField, self).__init__(
            MoneyIntervalForm, *args, **kwargs)

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
    is_other_adaptation = BooleanField(u'Any other adaptation')
    other_adaptation = TextAreaField(
        u'Any other adaptation',
        description=u'Please tell us what you need in the box below')


class PartnerMoneyField(MoneyField, PartnerMixin):
    pass


class DayChoiceField(SelectField):

    def __init__(self, num_days=6, *args, **kwargs):
        super(DayChoiceField, self).__init__(*args, **kwargs)
        self.choices = map(day_choice, available_days(num_days))


def parse_HHMM(s):
    if s:
        hour = int(s[:2])
        minute = int(s[2:])
        return datetime.time(hour, minute)
    return None


def parse_YYYYMMDD(s):
    if s:
        year = int(s[:4])
        month = int(s[4:6])
        day = int(s[6:])
        return datetime.date(year, month, day)
    return None


def scheduled_time(specific_day, time_today, time_tomorrow, day, time_in_day):
    date = datetime.date.today()
    time = None

    if specific_day == 'today':
        time = parse_HHMM(time_today)

    if specific_day == 'tomorrow':
        date += datetime.timedelta(days=1)
        time = parse_HHMM(time_tomorrow)

    if specific_day == 'specific_day':
        date = parse_YYYYMMDD(day)
        time = parse_HHMM(time_in_day)

    if date and time:
        return datetime.datetime.combine(date, time)

    return None


class AvailabilityCheckerForm(NoCsrfForm):
    specific_day = RadioField(
        label=u'Arrange a callback time',
        choices=DAY_CHOICES,
        default=DAY_CHOICES[0][0])

    # choices must be set dynamically as cache is not available at runtime
    time_today = SelectField(
        choices=(),
        id='id_time_today')
    time_tomorrow = SelectField(
        choices=(),
        id='id_time_tomorrow')
    time_in_day = SelectField(
        choices=(),
        id='id_time_in_day')
    day = DayChoiceField(id='id_day')

    def __init__(self, *args, **kwargs):
        kwargs['prefix'] = ''
        super(AvailabilityCheckerForm, self).__init__(*args, **kwargs)

        setattr(self._fields['time_today'], 'choices',
                map(time_choice, today_slots()))
        setattr(self._fields['time_tomorrow'], 'choices',
                map(time_choice, tomorrow_slots()))
        setattr(self._fields['time_in_day'], 'choices',
                map(time_choice, time_slots()))

    def validate(self):
        is_valid = super(AvailabilityCheckerForm, self).validate()
        time = scheduled_time(self.specific_day.data, self.time_today.data,
                              self.time_tomorrow.data, self.day.data,
                              self.time_in_day.data)
        if time is None:
            log.warning('Failed calculating scheduled_time. self.data = {0}'
                        .format(self.data))
            self.specific_day.errors = [u'There was a problem with the'
                                        u' selected time, please try again']
            is_valid = False

        validate_fields = (
            ('time_today', 'today'),
            ('time_tomorrow', 'tomorrow'),
            ('time_in_day', 'specific_day'),
        )

        for field_name, specific_day in validate_fields:
            if self.specific_day.data == specific_day and \
                    not available(time):
                self._fields[field_name].errors = [u'Can\'t schedule a callback'
                                                   u' at the requested time']
                is_valid = False

        if self.specific_day.data == 'specific_day':
            if not self.day.data:
                self.day.errors = [u'This field is required']
            if not available(time):
                self.day.errors = [u'Can\'t schedule a callback '
                                   u'on the requested day']

        return is_valid


class AvailabilityCheckerField(FormField):
    """Convenience class for FormField(AvailabilityCheckerForm"""

    widget = widgets.ListWidget()

    def __init__(self, *args, **kwargs):
        super(AvailabilityCheckerField, self).__init__(
            AvailabilityCheckerForm, *args, **kwargs)
