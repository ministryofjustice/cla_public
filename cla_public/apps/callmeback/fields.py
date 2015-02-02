# -*- coding: utf-8 -*-
"CallMeBack form fields"

import datetime
import random

from flask.ext.babel import lazy_gettext as _
import pytz
from wtforms import FormField, RadioField, SelectField
from wtforms import Form as NoCsrfForm
from wtforms.validators import InputRequired, ValidationError

from cla_common import call_centre_availability
from cla_common.call_centre_availability import OpeningHours
from cla_public.config import common as settings
from cla_public.apps.callmeback.constants import DAY_CHOICES, DAY_TODAY, \
    DAY_SPECIFIC
from cla_public.apps.checker.validators import IgnoreIf, FieldValueNot
from cla_public.libs.call_centre_availability import day_choice, time_choice


OPERATOR_HOURS = OpeningHours(**settings.OPERATOR_HOURS)


class FormattedChoiceField(object):
    """
    Mixin for fields applying a formatting function to values
    """

    def process_data(self, value):
        try:
            self.data = self._format(value)
        except ValueError:
            self.data = value

    def pre_validate(self, form):
        choice_values = (v for v, _ in self.choices)
        if self._format(self.data) not in choice_values:
            raise ValueError(self.gettext('Not a valid choice'))


class DayChoiceField(FormattedChoiceField, SelectField):
    """
    Select field with next `num_days` days as options
    """

    def __init__(self, num_days=6, *args, **kwargs):
        super(DayChoiceField, self).__init__(*args, **kwargs)
        self.choices = map(day_choice, OPERATOR_HOURS.available_days(num_days))

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
    """
    Select field with available time slots for a specific day as options
    """

    def __init__(self, choices_callback=None, validators=None, **kwargs):
        super(TimeChoiceField, self).__init__(validators=validators, **kwargs)
        self.choices = map(time_choice, choices_callback())
        self.default, display = random.choice(self.choices)

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
        time = datetime.datetime.combine(date, field.data)
        if not OPERATOR_HOURS.can_schedule_callback(time):
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
            AvailableSlot(DAY_TODAY)],
        id='id_time_today')
    day = DayChoiceField(
        validators=[
            IgnoreIf('specific_day', FieldValueNot(DAY_SPECIFIC)),
            InputRequired()],
        id='id_day')
    time_in_day = TimeChoiceField(
        OPERATOR_HOURS.time_slots,
        validators=[
            IgnoreIf('specific_day', FieldValueNot(DAY_SPECIFIC)),
            AvailableSlot(DAY_SPECIFIC)],
        id='id_time_in_day')

    def __init__(self, *args, **kwargs):
        kwargs['prefix'] = ''
        super(AvailabilityCheckerForm, self).__init__(*args, **kwargs)
        if not self.time_today.choices:
            self.specific_day.data = DAY_SPECIFIC

    def scheduled_time(self, today=None):
        """
        Get the datetime of the selected day and timeslot
        """
        date = today or datetime.date.today()
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
        return self.form.scheduled_time().replace(tzinfo=pytz.utc)
