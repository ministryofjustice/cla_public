# -*- coding: utf-8 -*-
"Base forms"

from flask import render_template, current_app, request

from flask_wtf import Form
from flask.ext.babel import lazy_gettext as _, get_translations
from wtforms import TextAreaField, RadioField, SelectMultipleField, \
    StringField, widgets, ValidationError
from wtforms.validators import InputRequired

from cla_public.apps.base.constants import FEEL_ABOUT_SERVICE, HELP_FILLING_IN_FORM, \
    REASONS_FOR_CONTACTING, REASONS_FOR_CONTACTING_OTHER, REASONS_FOR_CONTACTING_NONE
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


class ZendeskForm(Honeypot, BabelTranslationsFormMixin, Form):
    @classmethod
    def _make_referrer_field(cls, referrer_url):
        return {
            'id': 26047167,  # Referrer URL field
            'value': referrer_url,
        }

    def _make_api_payload(self, template, subject, group_id, tags, requester_id=None, custom_fields=None):
        user_agent = request.headers.get('User-Agent')
        comment_body = render_template(template, form=self, user_agent=user_agent)

        environment = current_app.config['CLA_ENV']
        if environment != 'prod':
            subject = '[TEST] - ' + subject

        ticket = {
            'requester_id': requester_id or current_app.config['ZENDESK_DEFAULT_REQUESTER'],
            'subject': subject,
            'comment': {
                'body': comment_body
            },
            'group_id': group_id,
            'tags': tags,
            'custom_fields': [{
                'id': 23791776,  # Browser field
                'value': user_agent,
            }],
        }
        if custom_fields:
            ticket['custom_fields'].extend(custom_fields)

        return {'ticket': ticket}


class FeedbackForm(ZendeskForm):
    referrer = StringField(
        widget=widgets.HiddenInput(),
        validators=[InputRequired()],
    )
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
        return self._make_api_payload(
            template='emails/zendesk-feedback.txt',
            subject='CLA Public Feedback',
            group_id=23832817,  # CLA Public
            tags=['feedback', 'civil_legal_advice_public'],
            custom_fields=[self._make_referrer_field(self.referrer.data)],
        )


class ReasonsForContactingForm(ZendeskForm):
    referrer = StringField(
        widget=widgets.HiddenInput(),
        validators=[InputRequired()],
    )
    reasons = SelectMultipleField(
        label=_(u'You can select more than one option:'),
        choices=REASONS_FOR_CONTACTING,
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput(),
    )
    other_reasons = TextAreaField(_(u'Other reasons'))

    REASONS_FOR_CONTACTING_OTHER = REASONS_FOR_CONTACTING_OTHER
    REASONS_FOR_CONTACTING_NONE = REASONS_FOR_CONTACTING_NONE

    def validate_reasons(self, field):
        if not field.data:
            raise ValidationError(u'You need to select at least one option')
        if REASONS_FOR_CONTACTING_NONE in field.data and len(field.data) > 1:
            raise ValidationError(u'You cannot select “%s” and other options together'
                                  % REASONS_FOR_CONTACTING_NONE)

    def validate_other_reasons(self, field):
        if REASONS_FOR_CONTACTING_OTHER in self.reasons.data and not field.data:
            raise ValidationError(u'Please specify the other reasons')

    def api_payload(self):
        return self._make_api_payload(
            template='emails/zendesk-reasons-for-contacting.txt',
            subject='CLA Public - Reasons for Contacting',
            group_id=25707197,  # CLA Public reasons for contacting
            tags=['reasons_for_contacting', 'civil_legal_advice_public'],
            custom_fields=[self._make_referrer_field(self.referrer.data)],
        )
