import datetime

from wtforms.compat import string_types
from wtforms.validators import StopValidation, ValidationError, Optional

from cla_public.apps.checker.constants import DAY_TODAY, DAY_TOMORROW, \
    DAY_SPECIFIC
from cla_public.libs import call_centre_availability
from cla_public.libs.call_centre_availability import available


class IgnoreIf(object):

    def __init__(self, field_name, dependencies, message=''):
        self.field_name = field_name
        self.message = message
        try:
            self.dependencies = [d for d in dependencies]
        except TypeError:
            self.dependencies = [dependencies]

    def __call__(self, form, field):
        depfield = getattr(form, self.field_name)
        for dependency in self.dependencies:
            if callable(dependency) and dependency(depfield, form=form):
                if not field.raw_data or isinstance(field.raw_data[0], string_types):
                    if hasattr(field, 'clear_errors'):
                        field.clear_errors()
                    else:
                        field.errors[:] = []
                raise StopValidation()


class FieldValue(object):

    def __init__(self, value):
        self.value = value

    def __call__(self, field, **kwargs):
        return field.data == self.value


class FieldValueNot(FieldValue):

    def __call__(self, field, **kwargs):
        return field.data != self.value


class AtLeastOne(object):
    """
    Valid if at least one option is checked.

    :param message:
        Error message to raise in case of a validation error.
    """

    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        if len(field.data) < 1:
            message = self.message
            if message is None:
                message = field.gettext('Must select at least one option.')
            raise ValidationError(message)


class MoneyIntervalAmountRequired(object):

    def __call__(self, form, field):
        amount = field.form.per_interval_value.data
        if amount is None:
            raise ValidationError(u'Please provide an amount')


class ValidMoneyInterval(object):
    """
    Validates that either an amount and interval have been set, or that a zero
    amount has been set.
    """

    def __call__(self, form, field):
        amount = field.form.per_interval_value
        interval = field.form.interval_period
        amount_not_set = amount.data is None
        nonzero_amount = amount.data > 0
        interval_selected = interval.data != ''

        try:
            amount.validate(field.form)
        except ValidationError as e:
            raise e

        if interval_selected and amount_not_set:
            raise ValidationError(u'Not a valid amount')

        if not interval_selected and nonzero_amount:
            raise ValidationError(u'Please select a time period from the drop down')


class AvailableSlot(object):
    """
    Validates whether the selected time slot is available.
    """

    def __init__(self, day):
        self.day = day

    def __call__(self, form, field):
        date = call_centre_availability.current_datetime()
        if self.day == DAY_TOMORROW:
            date = date + datetime.timedelta(days=1)
        if self.day == DAY_SPECIFIC:
            date = form.day.data
        time = datetime.datetime.combine(date, field.data)
        if not available(time):
            raise ValidationError(
                u"Can't schedule a callback at the requested time")


class NotRequired(Optional):
    field_flags = ()
