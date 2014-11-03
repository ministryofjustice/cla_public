# -*- coding: utf-8 -*-
"Checker forms"

from flask_wtf import Form
from wtforms import BooleanField, RadioField
from wtforms.validators import Required

from .constants import CATEGORIES, RESULT_OPTIONS


class HelpTextRadioField(RadioField):
    """RadioField that also stores an field for inline help text

    The choices kwargs field takes a list of triples.

    Format:

    choices=[(name, label, helptext), ...]
    """

    def __init__(self, *args, **kwargs):
        self.helptext = []
        choices = []
        for name, label, helptext in kwargs.get('choices', []):
            self.helptext.append(helptext)
            choices.append((name, label))
        if choices:
            kwargs['choices'] = choices
        super(HelpTextRadioField, self).__init__(*args, **kwargs)

    def __iter__(self):
        options = super(HelpTextRadioField, self).__iter__()
        for index, option in enumerate(options):
            option.helptext = self.helptext[index]
            yield option


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
