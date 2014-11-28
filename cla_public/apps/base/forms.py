# -*- coding: utf-8 -*-
"Base forms"

from flask_wtf import Form
from wtforms import StringField, TextAreaField
from cla_public.apps.base.fields import MultiRadioField

from cla_public.apps.base.constants import FEEL_ABOUT_SERVICE, \
    HELP_FILLING_IN_FORM
from cla_public.apps.checker.honeypot import Honeypot


class FeedbackForm(Honeypot, Form):
    difficulty = TextAreaField(u'Did you have any difficulty with this service?')

    ideas = TextAreaField(u'Do you have any ideas for how it could be improved?')

    feel_about_service = MultiRadioField(
        u'Overall, how did you feel about the service you received today?',
        choices=FEEL_ABOUT_SERVICE)

    help_filling_in_form = MultiRadioField(
        u'Did you have any help filling in this form?',
        choices=HELP_FILLING_IN_FORM)

