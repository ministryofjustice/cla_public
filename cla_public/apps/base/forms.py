# coding: utf-8
"Base forms"

from flask import render_template, current_app, request

from flask_wtf import Form
from flask.ext.babel import lazy_gettext as _, get_translations
from wtforms import TextAreaField, RadioField, SelectMultipleField, StringField, widgets
from wtforms.validators import InputRequired, Length

from cla_public.apps.base.constants import HELP_FILLING_IN_FORM, REASONS_FOR_CONTACTING_CHOICES, REASONS_FOR_CONTACTING
from cla_public.libs.honeypot import Honeypot


class BabelTranslations(object):
    def gettext(self, string):
        t = get_translations()
        if t is None:
            return string
        return t.ugettext(string)

    def ngettext(self, singular, plural, num):
        variables = {"num": num}
        t = get_translations()
        if t is None:
            return (singular if num == 1 else plural) % variables
        return t.ungettext(singular, plural, num) % variables


class BabelTranslationsFormMixin(object):
    def _get_translations(self):
        return BabelTranslations()


_textarea_length_validator = Length(max=1000, message=u"Field cannot contain more than %(max)d characters")


class FeedbackForm(Honeypot, BabelTranslationsFormMixin, Form):
    referrer = StringField(widget=widgets.HiddenInput())

    difficulty = TextAreaField(
        label=_(u"Did you have difficulty using this service? Tell us about the problem."),
        validators=[_textarea_length_validator],
    )

    ideas = TextAreaField(
        label=_(u"Do you have any ideas for how it could be improved?"), validators=[_textarea_length_validator]
    )

    help_filling_in_form = RadioField(
        _(u"Did you have any help filling in this form?"), choices=HELP_FILLING_IN_FORM, validators=[InputRequired()]
    )

    def api_payload(self):
        user_agent = request.headers.get("User-Agent")
        comment_body = render_template("emails/zendesk-feedback.txt", form=self, user_agent=user_agent)

        environment = current_app.config["CLA_ENV"]
        subject = "CLA Public Feedback"
        if environment != "production":
            subject = "[TEST] - " + subject

        ticket = {
            "requester_id": current_app.config["ZENDESK_DEFAULT_REQUESTER"],
            "subject": subject,
            "comment": {"body": comment_body},
            "group_id": 23832817,  # CLA Public
            "tags": ["feedback", "civil_legal_advice_public"],
            "custom_fields": [
                {"id": 23791776, "value": user_agent},  # Browser field
                {"id": 26047167, "value": self.referrer.data},  # Referrer URL field
            ],
        }

        return {"ticket": ticket}


class ReasonsForContactingForm(Honeypot, BabelTranslationsFormMixin, Form):
    """
    Interstitial form to ascertain why users are dropping out of
    the checker service
    """

    referrer = StringField(widget=widgets.HiddenInput())
    reasons = SelectMultipleField(
        label=_(u"You can select more than one option"),
        choices=REASONS_FOR_CONTACTING_CHOICES,
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput(),
    )
    other_reasons = TextAreaField(label=_(u"Please specify"), validators=[_textarea_length_validator])

    REASONS_FOR_CONTACTING_OTHER = REASONS_FOR_CONTACTING.OTHER

    def api_payload(self):
        return {
            "reasons": [{"category": category} for category in self.reasons.data],
            "other_reasons": self.other_reasons.data or "",
            "user_agent": request.headers.get("User-Agent") or "Unknown",
            "referrer": self.referrer.data or "Unknown",
        }
