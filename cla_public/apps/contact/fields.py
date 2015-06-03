# -*- coding: utf-8 -*-
"Contact form fields"
from collections import OrderedDict

import datetime
import random

from flask.ext.babel import lazy_gettext as _
from wtforms import FormField, RadioField, SelectField
from wtforms import Form as NoCsrfForm
from wtforms.validators import InputRequired, ValidationError

from cla_common import call_centre_availability
from cla_common.call_centre_availability import OpeningHours
from cla_public.config import common as settings
from cla_public.apps.contact.constants import DAY_CHOICES, DAY_TODAY, \
    DAY_SPECIFIC
from cla_public.apps.checker.validators import IgnoreIf, FieldValueNot
from cla_public.libs.call_centre_availability import day_choice, time_choice, \
    monday_before_11am_between_eod_friday_and_monday, monday_after_11_hours


OPERATOR_HOURS = OpeningHours(**settings.OPERATOR_HOURS)
OPERATOR_HOURS.day_hours.insert(0, (
    monday_before_11am_between_eod_friday_and_monday,
    monday_after_11_hours()
))


class FormattedChoiceField(object):
    """
    Mixin for fields applying a formatting function to values
    """

    def process_data(self, value):
        try:
            self.data = self._format(value)
        except ValueError:
            self.data = value

    def iter_choices(self):
        for value, label in self.choices:
            yield (value, label, self.coerce(value) == self._format(self.data))

    def pre_validate(self, form):
        choice_values = (v for v, _ in self.choices)
        if self._format(self.data) not in choice_values:
            raise ValueError(self.gettext('Not a valid choice'))


def time_slots_for_day(day):
    slots = OPERATOR_HOURS.time_slots(day)
    slots = filter(OPERATOR_HOURS.can_schedule_callback, slots)
    return map(time_choice, slots)


class DayChoiceField(FormattedChoiceField, SelectField):
    """
    Select field with next `num_days` days as options
    """

    def __init__(self, num_days=6, *args, **kwargs):
        super(DayChoiceField, self).__init__(*args, **kwargs)
        self.choices = map(day_choice, OPERATOR_HOURS.available_days(num_days))

    @property
    def day_time_choices(self, num_days=6):
        days = OPERATOR_HOURS.available_days(num_days)

        def time_slots(day):
            slots = OrderedDict(time_slots_for_day(day.date()))
            return (self._format(day), slots)

        return dict(map(time_slots, days))

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

    @classmethod
    def _format(cls, value):
        if value and not isinstance(value, basestring):
            return '{:%Y%m%d}'.format(value)
        return value


class TimeChoiceField(FormattedChoiceField, SelectField):
    """
    Select field with available time slots for a specific day as options
    """

    def __init__(self, choices_callback=None, validators=None, **kwargs):
        super(TimeChoiceField, self).__init__(validators=validators, **kwargs)
        self.choices = map(time_choice, choices_callback())
        if self.choices:
            self.default, _ = random.choice(self.choices)

    def set_day_choices(self, day):
        self.choices = time_slots_for_day(day)
        self.default, _ = random.choice(self.choices)

    def process_data(self, value):
        if isinstance(value, basestring):
            return self.process_formdata([value])
        self.data = value

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                hour = int(valuelist[0][:2])
                minute = int(valuelist[0][2:])
                self.data = datetime.time(hour, minute)
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid time'))

    @classmethod
    def _format(cls, value):
        if value and not isinstance(value, basestring):
            return '{:%H%M}'.format(value)
        return value


class AvailableSlot(object):
    """
    Validates whether the selected time slot is available.
    """

    def __init__(self, day):
        self.day = day

    def __call__(self, form, field):
        date = call_centre_availability.current_datetime()
        if self.day == DAY_SPECIFIC:
            date = form.day.data
        time = datetime.datetime.combine(date, field.data) if date else None
        if not (time and OPERATOR_HOURS.can_schedule_callback(time)):
            raise ValidationError(
                field.gettext(
                    u"Can't schedule a callback at the requested time"))


class AvailabilityCheckerForm(NoCsrfForm):
    """
    Subform allowing the user to select a time and date for a callback
    """
    specific_day = RadioField(
        label=_(u'Arrange a callback time'),
        choices=DAY_CHOICES,
        default=DAY_TODAY)

    # choices must be set dynamically as cache is not available at runtime
    time_today = TimeChoiceField(
        OPERATOR_HOURS.today_slots,
        validators=[
            IgnoreIf('specific_day', FieldValueNot(DAY_TODAY)),
            AvailableSlot(DAY_TODAY)])
    day = DayChoiceField(
        validators=[
            IgnoreIf('specific_day', FieldValueNot(DAY_SPECIFIC)),
            InputRequired()])
    time_in_day = TimeChoiceField(
        OPERATOR_HOURS.time_slots,
        validators=[
            IgnoreIf('specific_day', FieldValueNot(DAY_SPECIFIC)),
            AvailableSlot(DAY_SPECIFIC)])

    def __init__(self, *args, **kwargs):
        super(AvailabilityCheckerForm, self).__init__(*args, **kwargs)
        if not self.time_today.choices:
            self.specific_day.data = DAY_SPECIFIC

        day = datetime.datetime.strptime(self.day.choices[0][0], "%Y%m%d").date()
        self.time_in_day.set_day_choices(day)


    def scheduled_time(self, today=None):
        """
        Get the datetime of the selected day and timeslot
        """
        date = today or call_centre_availability.current_datetime().date()
        time = None

        if self.specific_day.data == DAY_TODAY:
            time = self.time_today.data

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

    @property
    def data(self):
        """
        Get the datetime of the selected day and timeslot
        """
        return self.scheduled_time()

    def scheduled_time(self):
        return self.form.scheduled_time()


class ValidatedFormField(FormField):
    def __init__(self, form_class, *args, **kwargs):
        self._errors = []
        self.validators = kwargs.pop('validators', [])

        super(ValidatedFormField, self).__init__(
            form_class, *args, **kwargs)

    def validate(self, form, extra_validators=None):
        if self._run_validation_chain(form, self.validators):
            return len(self.errors) == 0
        form_valid = self.form.validate()
        return form_valid and len(self.errors) == 0

    @property
    def errors(self):
        return self._errors + self.form.errors.items()

    @errors.setter
    def errors(self, _errors):
        self._errors = _errors
