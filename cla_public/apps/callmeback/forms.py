# -*- coding: utf-8 -*-
"CallMeBack forms"

from flask import session
from flask.ext.babel import lazy_gettext as _
from flask_wtf import Form
from wtforms import Form as NoCsrfForm
from wtforms import BooleanField, FormField, RadioField, SelectField, \
    StringField, TextAreaField
from wtforms.validators import InputRequired, Optional, Length

from cla_common.constants import ADAPTATION_LANGUAGES
from cla_public.apps.callmeback.fields import AvailabilityCheckerField, \
    ValidatedFormField
from cla_public.apps.checker.constants import CONTACT_SAFETY, CONTACT_PREFERENCE, \
    YES, NO
from cla_public.apps.base.forms import BabelTranslationsFormMixin
from cla_public.apps.checker.validators import NotRequired, IgnoreIf, FieldValue
from cla_public.libs.honeypot import Honeypot


LANG_CHOICES = filter(
    lambda x: x[0] not in ('ENGLISH', 'WELSH'),
    [('', _('-- Choose a language --'))] + ADAPTATION_LANGUAGES)


class AdaptationsForm(BabelTranslationsFormMixin, NoCsrfForm):
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


class RequestCallBackForm(BabelTranslationsFormMixin, NoCsrfForm):
    """
    Subform to request callback
    """
    contact_number = StringField(
        _(u'Contact phone number'),
        validators=[
            InputRequired(),
            Length(max=20, message=_(u'Your telephone number must be 20 '
                                     u'characters or less'))]
    )
    safe_to_contact = RadioField(
        _(u'Is it safe for us to leave a message on this number?'),
        choices=CONTACT_SAFETY,
        default='', # Backend doesn't accept `None` as valid value
        validators=[
            InputRequired(message=_(u'Please choose Yes or No'))],
    )
    time = AvailabilityCheckerField(
        _(u'Select a time for us to call you'),
        description=_(u'We will try to call you back around the time you '
                      u'request, but this may not always be possible. We will '
                      u'always call you back by the next working day.'))


class AddressForm(BabelTranslationsFormMixin, NoCsrfForm):
    """
    Subform for address fields
    """
    post_code = StringField(
        _(u'Postcode'),
        validators=[
            Length(max=12, message=_(u'Your postcode must be 12 characters '
                                     u'or less')),
            NotRequired()])
    street_address = TextAreaField(
        _(u'Street address'),
        validators=[
            Length(max=255, message=_(u'Your address must be 255 characters '
                                      u'or less')),
            NotRequired()])


class CallMeBackForm(Honeypot, BabelTranslationsFormMixin, Form):
    """
    Form to request a callback
    """
    full_name = StringField(
        _(u'Full name'),
        description=_(u'For example: John Smith'),
        validators=[
            Length(max=400, message=_(u'Your full name must be 400 '
                                      u'characters or less')),
            InputRequired()])
    callback_requested = RadioField(
        _(u'Contact preference'),
        choices=CONTACT_PREFERENCE,
        validators=[
            InputRequired(message=_(u'Please choose one of the options'))],
    )
    callback = ValidatedFormField(
        RequestCallBackForm,
        validators=[
            IgnoreIf('callback_requested', FieldValue(NO))
        ])
    address = ValidatedFormField(
        AddressForm,
        validators=[Optional()])
    extra_notes = TextAreaField(
        _(u'Help the operator to understand your situation'),
        description=(_(
            u"If you’d like to tell us more about your problem, please do so "
            u"in the box below. The Civil Legal Advice operator will read "
            u"this before they call you.")),
        validators=[
            Length(max=5000, message=_(u'Your notes must be 5000 characters '
                                       u'or less')),
            Optional()])
    adaptations = ValidatedFormField(
        AdaptationsForm,
        _(u'Do you have any special communication needs?'),
        validators=[Optional()])

    def api_payload(self):
        "Form data as data structure ready to send to API"
        data = {
            'personal_details': {
                'full_name': self.full_name.data,
                'postcode': self.address.form.post_code.data,
                'mobile_phone': self.callback.form.contact_number.data,
                'street': self.address.form.street_address.data,
                'safe_to_contact': self.callback.form.safe_to_contact.data
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
            }
        }
        if self.callback_requested.data == YES:
            data['requires_action_at'] = self.callback.form.time.scheduled_time().isoformat()

        return data
