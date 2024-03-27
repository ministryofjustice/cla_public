# coding: utf-8
"Contact form fields"
from collections import OrderedDict

import datetime

from flask import current_app
from flask.ext.babel import lazy_gettext as _
from wtforms import FormField, RadioField, SelectField
from wtforms import Form as NoCsrfForm
from wtforms.validators import ValidationError, InputRequired

from cla_common import call_centre_availability
from cla_common.call_centre_availability import OpeningHours
from cla_common.constants import OPERATOR_HOURS as CALL_CENTRE_OPERATOR_HOURS
from cla_public.apps.contact.helper import append_default_option_to_list
from cla_public.apps.contact.constants import (
    DAY_CHOICES,
    DAY_TODAY,
    DAY_SPECIFIC,
    SELECT_DATE_OPTION_DEFAULT,
    SELECT_TIME_OPTION_DEFAULT,
    TIME_TODAY_VALIDATION_ERROR,
    DAY_SPECIFIC_VALIDATION_ERROR,
    TIME_SPECIFIC_VALIDATION_ERROR,
)
from cla_public.apps.checker.validators import IgnoreIf, FieldValueNot
from cla_public.libs.call_centre_availability import format_date_option, format_time_option
from cla_public.apps.contact.api import get_valid_callback_days, get_valid_callback_timeslots_on_date

OPERATOR_HOURS = OpeningHours(**CALL_CENTRE_OPERATOR_HOURS)


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
        if isinstance(form, AvailabilityCheckerForm):
            return True  # This is validated using AvailableSlot
        choice_values = (v for v, _ in self.choices)
        if self._format(self.data) not in choice_values:
            raise ValueError(self.gettext("Not a valid choice"))


def time_slots_for_day(day, is_third_party_callback=False):
    if current_app.config.get("USE_BACKEND_CALLBACK_SLOTS", False):
        slots = get_valid_callback_timeslots_on_date(day, is_third_party_callback)
    else:
        slots = OPERATOR_HOURS.time_slots(day)
        slots = filter(OPERATOR_HOURS.can_schedule_callback, slots)
    return map(format_time_option, slots)


class DayChoiceField(FormattedChoiceField, SelectField):
    """
    Select field with next `num_days` days as options
    """

    def __init__(self, third_party_callback=False, num_days=6, *args, **kwargs):
        super(DayChoiceField, self).__init__(*args, **kwargs)
        self.is_third_party_callback = third_party_callback
        self.valid_days = (
            get_valid_callback_days(include_today=False, is_third_party_callback=self.is_third_party_callback)
            if current_app.config.get("USE_BACKEND_CALLBACK_SLOTS", False)
            else OPERATOR_HOURS.available_days(num_days)
        )
        self.choices = map(format_date_option, self.valid_days)
        append_default_option_to_list(self.choices, SELECT_DATE_OPTION_DEFAULT)
        self.day_choices = map(format_date_option, self.valid_days)

    @property
    def day_time_choices(self):
        # Generate time slots options for call on another day select options

        def time_slots(day):
            slots = OrderedDict(time_slots_for_day(day.date(), self.is_third_party_callback))
            return (self._format(day), slots)

        return dict(map(time_slots, self.valid_days))

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                year = int(valuelist[0][:4])
                month = int(valuelist[0][4:6])
                day = int(valuelist[0][6:])
                self.data = datetime.date(year, month, day)
            except ValueError:
                self.data = None
                raise ValueError(self.gettext("Not a valid date"))

    @classmethod
    def _format(cls, value):
        if isinstance(value, (datetime.date, datetime.datetime)):
            return "{:%Y%m%d}".format(value)
        return value


class TimeChoiceField(FormattedChoiceField, SelectField):
    """
    Select field with available time slots for a specific day as options
    """

    def __init__(self, choices_callback=None, third_party_callback=False, validators=None, **kwargs):
        super(TimeChoiceField, self).__init__(validators=validators, **kwargs)
        self.is_third_party_callback = third_party_callback
        valid_slots = (
            get_valid_callback_timeslots_on_date(
                datetime.date.today(), is_third_party_callback=self.is_third_party_callback
            )
            if current_app.config.get("USE_BACKEND_CALLBACK_SLOTS", False)
            else choices_callback()
        )
        self.choices = map(format_time_option, valid_slots)
        if self.choices:
            append_default_option_to_list(self.choices, SELECT_TIME_OPTION_DEFAULT)

    def set_day_choices(self, day):
        self.choices = time_slots_for_day(day, self.is_third_party_callback)
        if self.choices:
            append_default_option_to_list(self.choices, SELECT_TIME_OPTION_DEFAULT)

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
                raise ValueError(self.gettext("Not a valid time"))

    @classmethod
    def _format(cls, value):
        if isinstance(value, datetime.time):
            return "{:%H%M}".format(value)
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
        # If user selects the default pre-fix "please select" option
        if field.data is None:
            raise ValidationError([field.gettext(u"Not a valid time")])
        time = datetime.datetime.combine(date, field.data) if date else None
        if not (time and OPERATOR_HOURS.can_schedule_callback(time)):
            raise ValidationError([field.gettext(u"Can’t schedule a callback at the requested time")])


class AvailabilityCheckerForm(NoCsrfForm):
    """
    Subform allowing the user to select a time and date for a callback
    """

    specific_day = RadioField(label=_(u"Arrange a callback time"), choices=DAY_CHOICES, default=DAY_TODAY)

    # choices must be set dynamically as cache is not available at runtime
    time_today = TimeChoiceField(
        choices_callback=OPERATOR_HOURS.today_slots,
        validators=[
            IgnoreIf("specific_day", FieldValueNot(DAY_TODAY)),
            InputRequired(message=_(TIME_TODAY_VALIDATION_ERROR)),
            AvailableSlot(DAY_TODAY),
        ],
    )
    day = DayChoiceField(
        validators=[
            IgnoreIf("specific_day", FieldValueNot(DAY_SPECIFIC)),
            InputRequired(message=_(DAY_SPECIFIC_VALIDATION_ERROR)),
        ]
    )
    time_in_day = TimeChoiceField(
        choices_callback=OPERATOR_HOURS.time_slots,
        validators=[
            IgnoreIf("specific_day", FieldValueNot(DAY_SPECIFIC)),
            InputRequired(message=_(TIME_SPECIFIC_VALIDATION_ERROR)),
            AvailableSlot(DAY_SPECIFIC),
        ],
    )

    def __init__(self, *args, **kwargs):
        super(AvailabilityCheckerForm, self).__init__(*args, **kwargs)
        if not self.time_today.choices:
            self.specific_day.data = DAY_SPECIFIC

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


class ThirdPartyAvailabilityCheckerForm(AvailabilityCheckerForm):
    time_today = TimeChoiceField(
        choices_callback=OPERATOR_HOURS.today_slots,
        third_party_callback=True,
        validators=[
            IgnoreIf("specific_day", FieldValueNot(DAY_TODAY)),
            InputRequired(message=_(TIME_TODAY_VALIDATION_ERROR)),
            AvailableSlot(DAY_TODAY),
        ],
    )
    day = DayChoiceField(
        third_party_callback=True,
        validators=[
            IgnoreIf("specific_day", FieldValueNot(DAY_SPECIFIC)),
            InputRequired(message=_(DAY_SPECIFIC_VALIDATION_ERROR)),
        ],
    )
    time_in_day = TimeChoiceField(
        choices_callback=OPERATOR_HOURS.time_slots,
        third_party_callback=True,
        validators=[
            IgnoreIf("specific_day", FieldValueNot(DAY_SPECIFIC)),
            InputRequired(message=_(TIME_SPECIFIC_VALIDATION_ERROR)),
            AvailableSlot(DAY_SPECIFIC),
        ],
    )


class AvailabilityCheckerField(FormField):
    """Convenience class for FormField(AvailabilityCheckerForm"""

    def __init__(self, *args, **kwargs):
        super(AvailabilityCheckerField, self).__init__(AvailabilityCheckerForm, *args, **kwargs)

    @property
    def data(self):
        """
        Get the datetime of the selected day and timeslot
        """
        return self.scheduled_time()

    def scheduled_time(self):
        return self.form.scheduled_time()


class ThirdPartyAvailabilityCheckerField(AvailabilityCheckerField):
    def __init__(self, *args, **kwargs):
        super(AvailabilityCheckerField, self).__init__(ThirdPartyAvailabilityCheckerForm, *args, **kwargs)


class ValidatedFormField(FormField):
    def __init__(self, form_class, *args, **kwargs):
        self._errors = []
        self.validators = kwargs.pop("validators", [])

        super(ValidatedFormField, self).__init__(form_class, *args, **kwargs)

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
