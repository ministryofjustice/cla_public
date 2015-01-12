# -*- coding: utf-8 -*-
"CallMeBack forms"

from flask import session
from flask.ext.babel import lazy_gettext as _, gettext
from flask_wtf import Form
from wtforms import Form as NoCsrfForm
from wtforms import BooleanField, FormField, RadioField, SelectField, \
    StringField, TextAreaField
from wtforms.validators import InputRequired, Optional

from cla_common.constants import ADAPTATION_LANGUAGES
from cla_public.apps.callmeback.constants import DAY_CHOICES, \
    DAY_TOMORROW, DAY_SPECIFIC
from cla_public.apps.callmeback.fields import AvailabilityCheckerField
from cla_public.apps.checker.constants import CONTACT_SAFETY
from cla_public.libs.honeypot import Honeypot


LANG_CHOICES = filter(
    lambda x: x[0] not in ('ENGLISH', 'WELSH'),
    [('', _('-- Choose a language --'))] + ADAPTATION_LANGUAGES)


class AdaptationsForm(NoCsrfForm):
    """
    Subform for adaptations
    """
    bsl_webcam = BooleanField(_(u'BSL - Webcam'))
    minicom = BooleanField(_(u'Minicom'))
    text_relay = BooleanField(_(u'Text Relay'))
    welsh = BooleanField(_(u'Welsh'))
    is_other_language = BooleanField(_(u'Other language'))
    other_language = SelectField(
        _(u'Language required:'),
        choices=(LANG_CHOICES))
    is_other_adaptation = BooleanField(_(u'Any other communication needs'))
    other_adaptation = TextAreaField(
        _(u'Other communication needs'),
        description=_(u'Please tell us what you need in the box below'))


class CallMeBackForm(Honeypot, Form):
    """
    Form to request a callback
    """
    full_name = StringField(
        _(u'Full name'),
        description=_(u'For example: John Smith'),
        validators=[InputRequired()])
    contact_number = StringField(
        _(u'Contact phone number'),
        validators=[InputRequired()])
    safe_to_contact = RadioField(
        _(u'Is it safe for us to leave a message on this number?'),
        choices=CONTACT_SAFETY,
        validators=[
            InputRequired(message=gettext(u'Please choose Yes or No'))],
    )
    post_code = StringField(_(u'Postcode'))
    address = TextAreaField(_(u'Address'))
    extra_notes = TextAreaField(
        _(u'Help the operator to understand your situation'),
        description=(_(
            u"If you’d like to tell us more about your problem, please do so "
            u"in the box below. The Civil Legal Advice operator will read "
            u"this before they call you.")),
        validators=[Optional()])
    adaptations = FormField(
        AdaptationsForm,
        _(u'Do you have any special communication needs?'))

    time = AvailabilityCheckerField(_(u'Select a time for us to call you'))

    def validate(self):
        """
        Put the callback time into the session on success
        """
        valid = super(CallMeBackForm, self).validate()
        if valid:
            session['time_to_callback'] = self.time.scheduled_time()
        return valid

    def api_payload(self):
        "Form data as data structure ready to send to API"
        return {
            'personal_details': {
                'full_name': self.full_name.data,
                'postcode': self.post_code.data,
                'mobile_phone': self.contact_number.data,
                'street': self.address.data,
                'safe_to_contact': self.safe_to_contact.data
            },
            'adaptation_details': {
                'bsl_webcam': self.adaptations.bsl_webcam.data,
                'minicom': self.adaptations.minicom.data,
                'text_relay': self.adaptations.text_relay.data,
                'language':
                    self.adaptations.welsh.data and 'WELSH'
                    or self.adaptations.other_language.data,
                'notes': self.adaptations.other_adaptation.data
                    if self.adaptations.is_other_adaptation.data else ''
            },
            'requires_action_at': self.time.data.isoformat(),
        }
