from wtforms.validators import StopValidation, ValidationError


class DependantOn(object):

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
            if callable(dependency) and not dependency(depfield, form=form):
                if hasattr(field, 'clear_errors'):
                    field.clear_errors()
                else:
                    field.errors = []
                raise StopValidation()


class FieldValue(object):

    def __init__(self, value):
        self.value = value

    def __call__(self, field, **kwargs):
        return field.data == self.value


class FieldValid(object):

    def __call__(self, field, form=None):
        return field.validate(form)


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
        data = field.data
        if 'amount' not in data or data['amount'] < 0:
            field.errors[:] = []
            raise ValidationError(u'Please provide an amount')
