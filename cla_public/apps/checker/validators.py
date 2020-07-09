# coding: utf-8
"Custom validators"
# TODO - none of this is exclusive to checker app

from wtforms.compat import string_types
from wtforms.validators import StopValidation, ValidationError, Optional


class IgnoreIf(object):
    def __init__(self, field_name, dependencies, message=""):
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
                    if hasattr(field, "clear_errors"):
                        field.clear_errors()
                    else:
                        if isinstance(field.errors, list):
                            field.errors[:] = []
                        else:
                            field.errors = []
                raise StopValidation()


class FieldValue(object):
    def __init__(self, value):
        self.value = value

    def __call__(self, field, **kwargs):
        return field.data == self.value


class FieldValueOrNone(FieldValue):
    def __call__(self, field, **kwargs):
        return field.data == self.value or not field.raw_data


class FieldValueNot(FieldValue):
    def __call__(self, field, **kwargs):
        return field.data != self.value


class FieldValueIn(FieldValue):
    def __call__(self, field, **kwargs):
        return self.value in field.data


class FieldValueNotIn(FieldValue):
    def __call__(self, field, **kwargs):
        return field.data is None or self.value not in field.data


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
                message = field.gettext("Select at least one option")
            raise ValidationError(message)


class MoneyIntervalAmountRequired(object):

    interval_texts = {
        "per_week": u"each week",
        "per_4week": u"every 4 weeks",
        "per_month": u"each month",
        "per_year": u"each year",
    }

    def __init__(self, message=None, freq_message=None, amount_message=None):
        self.message = message
        self.freq_message = freq_message
        self.amount_message = amount_message

    def __call__(self, form, field):
        amount = field.form.per_interval_value
        interval = field.form.interval_period
        amount_field_is_blank = not amount.errors and amount.data is None
        specific_period_error_message = interval.data != "" and self.amount_message

        if amount_field_is_blank:
            if specific_period_error_message:
                message = self.amount_message + " " + field.gettext(interval_texts[interval.data])
            else:
                message = self.message or field.gettext(u"Type in a number")
            raise StopValidation(message)

        if interval.data == "" and amount.data > 0 and self.freq_message:
            raise StopValidation(self.freq_message)


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
        interval_selected = interval.data != ""

        if amount.errors:
            raise ValidationError(amount.errors[0])

        if interval_selected and amount_not_set:
            raise ValidationError(field.gettext(u"Type in a number"))

        if not interval_selected and nonzero_amount:
            raise ValidationError(field.gettext(u"Select a time period from the drop down"))


class NotRequired(Optional):
    field_flags = ()


class ZeroOrMoreThan(object):
    def __init__(self, minvalue):
        self.minvalue = minvalue

    def __call__(self, form, field):
        if field.data != 0 and field.data <= self.minvalue:
            raise ValidationError(field.gettext(u"Enter 0 if you have no valuable items worth over £500 each"))
