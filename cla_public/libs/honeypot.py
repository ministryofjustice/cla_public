from wtforms import StringField, widgets
from wtforms.fields.core import UnboundField
from flask.ext.babel import lazy_gettext as _


# This should be something a bot would want to fill in
FIELD_NAME = "comment"


class HoneypotWidget(widgets.Input):
    def __call__(self, field, **kwargs):
        kwargs.setdefault("value", "")
        kwargs.setdefault("id", FIELD_NAME)

        return widgets.HTMLString("<input {params}>".format(params=widgets.html_params(name=field.name, **kwargs)))


class HoneypotField(StringField):
    widget = HoneypotWidget()

    def pre_validate(self, form):
        if self.data:
            raise ValueError(self.gettext(u"This field must be left empty"))


class Honeypot(object):
    def __init__(self, *args, **kwargs):

        unbound = UnboundField(HoneypotField, _(u"Leave this field empty"))
        self._unbound_fields.append((FIELD_NAME, unbound))

        super(Honeypot, self).__init__(*args, **kwargs)
