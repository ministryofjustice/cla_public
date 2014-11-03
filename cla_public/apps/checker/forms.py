# -*- coding: utf-8 -*-
"Checker forms"

from flask_wtf import Form
from wtforms import BooleanField, RadioField
from wtforms.validators import Required

from .constants import CATEGORIES, RESULT_OPTIONS


class HelpTextRadioField(RadioField):
    """RadioField that also stores an field for inline help text

    The choices kwargs field now takes a list of triples instead of a list of
    tuples.

    Format:

    choices=[(name, label, helptext), ...]
    """

    def __iter__(self):
        opts = {
            'widget': self.option_widget,
            '_name': self.name,
            '_form': None,
            '_meta': self.meta
        }
        for i, (value, label, helptext, checked) in enumerate(self.iter_choices()):
            opt = self._Option(label=label, id='%s-%d' % (self.id, i), **opts)

            # We shim the helptext in on the Option() object
            opt.helptext = helptext
            opt.process(None, value)
            opt.checked = checked
            yield opt

    def iter_choices(self):
        # We assume the choices field now has triples
        for value, label, helptext in self.choices:
            yield (value, label, helptext, self.coerce(value) == self.data)

    def pre_validate(self, form):
        for v, _, _ in self.choices:
            if self.data == v:
                break
        else:
            raise ValueError(self.gettext(u'Not a valid choice'))


class ProblemForm(Form):
    categories = HelpTextRadioField(
        u'What do you need help with?',
        choices=CATEGORIES,
        coerce=unicode,
        validators=[Required()])


class ProceedForm(Form):
    proceed = BooleanField(validators=[Required(u'Not a valid choice')])


class ResultForm(Form):
    result = RadioField(
        choices=RESULT_OPTIONS,
        validators=[Required(u'Not a valid choice')])
