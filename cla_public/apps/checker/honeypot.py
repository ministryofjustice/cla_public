from wtforms import StringField, widgets
from wtforms.fields.core import UnboundField


# This should be something a bot would want to fill in
FIELD_NAME = 'comment'

# The CSS class name used to hide the field
CSS_CLASS = 'hp_decoy'


class HoneypotException(Exception):
    pass


class HoneypotWidget(widgets.Input):

    def __call__(self, field, **kwargs):
        kwargs.setdefault('value', '')
        kwargs.setdefault('class_', CSS_CLASS)

        return widgets.HTMLString('<input {params}></input>'.format(
            params=widgets.html_params(
                name=field.name,
                **kwargs)))


class HoneypotField(StringField):
    widget = HoneypotWidget()


class Honeypot(object):

    def __init__(self, *args, **kwargs):

        unbound = UnboundField(
            HoneypotField,
            u'Leave this field empty')
        self._unbound_fields.append((FIELD_NAME, unbound))

        super(Honeypot, self).__init__(*args, **kwargs)

    def validate(self):
        field = getattr(self, FIELD_NAME)

        if field and field.data:
            raise HoneypotException('User filled the honeypot field')

        return super(Honeypot, self).validate()
