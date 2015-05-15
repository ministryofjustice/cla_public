# -*- coding: utf-8 -*-
"Base forms"

from flask import render_template, current_app

from flask_wtf import Form
from flask.ext.babel import lazy_gettext as _, get_translations
from wtforms import TextAreaField, RadioField
from wtforms.validators import InputRequired

from cla_public.apps.base.constants import FEEL_ABOUT_SERVICE, \
    HELP_FILLING_IN_FORM
from cla_public.libs.honeypot import Honeypot


class BabelTranslations(object):
    def gettext(self, string):
        t = get_translations()
        if t is None:
            return string
        return t.ugettext(string)

    def ngettext(self, singular, plural, num):
        variables = {'num': num}
        t = get_translations()
        if t is None:
            return (singular if num == 1 else plural) % variables
        return t.ungettext(singular, plural, num) % variables


class BabelTranslationsFormMixin(object):
    def _get_translations(self):
        return BabelTranslations()


class FeedbackForm(Honeypot, BabelTranslationsFormMixin, Form):
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
        environment = current_app.config['CLA_ENV']
        comment_body = render_template('emails/zendesk-feedback.txt', form=self)
        subject = 'CLA Public Feedback'

        if environment != 'prod':
            subject = '[TEST] - ' + subject

        return {
            'ticket': {
                'requester_id': 649762516,
                'subject': subject,
                'comment': {
                    'body': comment_body
                },
                'group_id': 23832817,
                'tags': ['feedback', 'civil_legal_advice_public'],
            }
        }
