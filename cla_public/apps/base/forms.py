# -*- coding: utf-8 -*-
"Base forms"

import requests
import json

from flask import render_template

from flask_wtf import Form
from flask.ext.babel import lazy_gettext as _, gettext, ngettext
from wtforms import StringField, TextAreaField, RadioField
from wtforms.validators import InputRequired

from cla_public.apps.base.constants import FEEL_ABOUT_SERVICE, \
    HELP_FILLING_IN_FORM
from cla_public.libs.honeypot import Honeypot


class BabelTranslations(object):
    def gettext(self, string):
        return gettext(string)

    def ngettext(self, singular, plural, n):
        return ngettext(singular, plural, n)


class BabelTranslationsFormMixin(object):
    def _get_translations(self):
        return BabelTranslations()


class FeedbackForm(Honeypot, Form, BabelTranslationsFormMixin):
    difficulty = TextAreaField(_(u'Did you have any difficulty with this service?'))

    ideas = TextAreaField(_(u'Do you have any ideas for how it could be improved?'))

    feel_about_service = RadioField(
        _(u'Overall, how did you feel about the service you received today?'),
        choices=FEEL_ABOUT_SERVICE,
        validators=[InputRequired()])

    help_filling_in_form = RadioField(
        _(u'Did you have any help filling in this form?'),
        choices=HELP_FILLING_IN_FORM,
        validators=[InputRequired()])

    def api_payload(self):
        comment_body = render_template('zendesk-feedback.txt', form=self)
        return {
            'ticket': {
                'requester_id': 649762516,
                'subject': 'CLA Public Feedback',
                'comment': {
                    'body': comment_body
                },
                'group_id': 23832817,
                'tags': ['feedback'],
            }
        }
