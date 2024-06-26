# coding: utf-8
"Contact forms"

from flask import current_app
from flask.ext.babel import lazy_gettext as _
from flask_wtf import Form
import pytz
from wtforms import Form as NoCsrfForm
from wtforms import BooleanField, RadioField, SelectField, StringField, TextAreaField
from wtforms.validators import InputRequired, Optional, Required, Length

from cla_common.constants import ADAPTATION_LANGUAGES, THIRDPARTY_RELATIONSHIP, CALLBACK_TYPES
from cla_public.apps.contact.fields import (
    AvailabilityCheckerField,
    ValidatedFormField,
    ThirdPartyAvailabilityCheckerField,
)
from cla_public.apps.checker.constants import (
    SAFE_TO_CONTACT,
    CONTACT_PREFERENCE,
    CONTACT_PREFERENCE_NO_CALLBACK,
    ANNOUNCE_PREFERENCE,
)
from cla_public.apps.base.forms import BabelTranslationsFormMixin
from cla_public.apps.checker.validators import IgnoreIf, FieldValue
from cla_public.apps.contact.validators import EmailValidator
from cla_public.apps.contact.constants import SELECT_OPTION_DEFAULT
from cla_public.libs.honeypot import Honeypot
from cla_public.libs.utils import get_locale
from cla_public.apps.contact.api import get_valid_callback_days


LANG_CHOICES = filter(lambda x: x[0] not in ("ENGLISH", "WELSH"), [("", "")] + ADAPTATION_LANGUAGES)

THIRDPARTY_RELATIONSHIP = map(lambda relationship: (relationship[0], _(relationship[1])), THIRDPARTY_RELATIONSHIP)
THIRDPARTY_RELATIONSHIP_CHOICES = SELECT_OPTION_DEFAULT + THIRDPARTY_RELATIONSHIP


class AdaptationsForm(BabelTranslationsFormMixin, NoCsrfForm):
    """
    Subform for adaptations
    """

    bsl_webcam = BooleanField(_(u"British Sign Language – webcam"))
    bsl_email = StringField(
        _(u"Enter your email address so we can arrange a BSL call"),
        validators=[
            IgnoreIf("bsl_webcam", FieldValue(False)),
            Length(max=255, message=_(u"Your address must be 255 characters or less")),
            EmailValidator(message=_(u"Enter an email address.")),
        ],
    )
    minicom = BooleanField(_(u"Minicom – for textphone users"))
    text_relay = BooleanField(_(u"Text Relay – for people with hearing or speech impairments"))
    welsh = BooleanField(_(u"Welsh"))
    is_other_language = BooleanField(_(u"Other language"))
    other_language = SelectField(_(u"Choose a language"), choices=(LANG_CHOICES))
    is_other_adaptation = BooleanField(_(u"Any other communication needs"))
    other_adaptation = TextAreaField(
        _(u"Other communication needs"),
        description=_(u"Please tell us what you need in the box below"),
        validators=[
            IgnoreIf("is_other_adaptation", FieldValue(False)),
            Length(max=4000, message=_(u"Your other communication needs must be 4000 characters or fewer")),
            Optional(),
        ],
    )

    def __init__(self, formdata=None, obj=None, prefix="", data=None, meta=None, **kwargs):
        if data is None:
            data = {"welsh": get_locale()[:2] == "cy"}
        if formdata is not None:
            is_bsl = formdata.get("adaptations-bsl_webcam")
            email = formdata.get("adaptations-bsl_email") or formdata.get("email")
            if is_bsl and email:
                formdata["adaptations-bsl_email"] = email
        super(AdaptationsForm, self).__init__(formdata, obj, prefix, data, meta, **kwargs)


class CallBackForm(BabelTranslationsFormMixin, NoCsrfForm):
    """
    Subform to request callback
    """

    contact_number = StringField(
        _(u"Phone number for the callback"),
        description=_(u"Enter the full number, including the area code. For example, 01632 960 1111."),
        validators=[
            InputRequired(message=_(u"Tell us what number to ring")),
            Length(max=20, message=_(u"Your telephone number must be 20 characters or less")),
        ],
    )
    time = AvailabilityCheckerField(label=_(u"Select a time for us to call"))

    announce_call_from_cla = RadioField(
        _(u"Can we say that we're calling from Civil Legal Advice?"),
        choices=ANNOUNCE_PREFERENCE,
        validators=[InputRequired(message=_(u"Select if we can say that we’re calling from Civil Legal Advice"))],
    )


class ThirdPartyForm(BabelTranslationsFormMixin, NoCsrfForm):
    """
    Subform for thirdparty callback
    """

    full_name = StringField(
        _(u"Full name of the person to call"),
        validators=[
            Length(max=400, message=_(u"Their full name must be 400 characters or less")),
            InputRequired(message=_(u"Tell us the name of the person to call")),
        ],
    )
    relationship = SelectField(
        _(u"Relationship to you"),
        choices=(THIRDPARTY_RELATIONSHIP_CHOICES),
        validators=[Required(message=_(u"Tell us how you know this person"))],
    )
    contact_number = StringField(
        _(u"Phone number for the callback"),
        description=_(u"Enter the full number, including the area code. For example, 01632 960 1111."),
        validators=[
            InputRequired(message=_(u"Tell us what number to ring")),
            Length(max=20, message=_(u"Your telephone number must be 20 characters or less")),
        ],
    )
    time = ThirdPartyAvailabilityCheckerField(label=_(u"Select a time for us to call"))


class AddressForm(BabelTranslationsFormMixin, NoCsrfForm):
    """
    Subform for address fields
    """

    post_code = StringField(
        _(u"Postcode"),
        validators=[Length(max=12, message=_(u"Your postcode must be 12 characters " u"or less")), Optional()],
    )
    street_address = TextAreaField(
        _(u"Street address"),
        validators=[Length(max=255, message=_(u"Your address must be 255 characters " u"or less")), Optional()],
    )


class ContactForm(Honeypot, BabelTranslationsFormMixin, Form):
    """
    Form to contact CLA
    """

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        if current_app.config.get("USE_BACKEND_CALLBACK_SLOTS", False):
            self.update_contact_preference()

    full_name = StringField(
        _(u"Your full name"),
        validators=[
            Length(max=400, message=_(u"Your full name must be 400 characters or less")),
            InputRequired(message=_(u"Tell us your name")),
        ],
    )

    contact_type = RadioField(
        _(u"Select a contact option"),
        choices=CONTACT_PREFERENCE,
        validators=[InputRequired(message=_(u"Tell us how we should get in contact"))],
    )

    def update_contact_preference(self):
        # If there are no callback slots available when the contact_type field is called the callback option should be removed.
        callback_slots_available = len(get_valid_callback_days()) != 0
        self.contact_type.choices = CONTACT_PREFERENCE if callback_slots_available else CONTACT_PREFERENCE_NO_CALLBACK

    callback = ValidatedFormField(
        CallBackForm,
        validators=[IgnoreIf("contact_type", FieldValue("call")), IgnoreIf("contact_type", FieldValue("thirdparty"))],
    )
    thirdparty = ValidatedFormField(
        ThirdPartyForm,
        validators=[IgnoreIf("contact_type", FieldValue("call")), IgnoreIf("contact_type", FieldValue("callback"))],
    )
    email = StringField(
        _(u"Email"),
        description=_(u"We will use this to send your reference number."),
        validators=[
            Length(max=255, message=_(u"Your address must be 255 characters or less")),
            EmailValidator(message=_(u"Invalid email address")),
            Optional(),
        ],
    )
    address = ValidatedFormField(AddressForm)
    extra_notes = TextAreaField(
        _(u"Tell us more about your problem"),
        validators=[Length(max=4000, message=_(u"Your notes must be 4000 characters or less")), Optional()],
    )
    adaptations = ValidatedFormField(AdaptationsForm, _(u"Do you have any special communication needs? (optional)"))

    def get_email(self):
        return self.email.data or self.adaptations.bsl_email.data

    def api_payload(self):
        "Form data as data structure ready to send to API"

        def process_selected_time(form_time):
            # all time slots are timezone naive (local time)
            # so we convert them to UTC for the backend
            naive = form_time.scheduled_time()
            local_tz = pytz.timezone(current_app.config["TIMEZONE"])
            local = local_tz.localize(naive)
            return local.astimezone(pytz.utc).isoformat()

        safe_to_contact = SAFE_TO_CONTACT if self.contact_type.data == CONTACT_PREFERENCE.CALLBACK else ""

        data = {
            "personal_details": {
                "full_name": self.full_name.data,
                "email": self.get_email(),
                "postcode": self.address.form.post_code.data,
                "mobile_phone": self.callback.form.contact_number.data,
                "street": self.address.form.street_address.data,
                "safe_to_contact": safe_to_contact,
                "announce_call": True,
            },
            "adaptation_details": {
                "bsl_webcam": self.adaptations.bsl_webcam.data,
                "minicom": self.adaptations.minicom.data,
                "text_relay": self.adaptations.text_relay.data,
                "language": self.adaptations.welsh.data and "WELSH" or self.adaptations.other_language.data,
                "notes": self.adaptations.other_adaptation.data if self.adaptations.is_other_adaptation.data else "",
            },
        }
        if self.contact_type.data == "callback":
            data["requires_action_at"] = process_selected_time(self.callback.form.time)
            data["personal_details"]["announce_call"] = self.callback.form.announce_call_from_cla.data
            data["callback_type"] = CALLBACK_TYPES.CHECKER_SELF

        if self.contact_type.data == "thirdparty":
            data["thirdparty_details"] = {"personal_details": {}}
            data["thirdparty_details"]["personal_details"]["full_name"] = self.thirdparty.full_name.data
            data["thirdparty_details"]["personal_details"]["mobile_phone"] = self.thirdparty.contact_number.data
            data["thirdparty_details"]["personal_details"]["safe_to_contact"] = SAFE_TO_CONTACT
            data["thirdparty_details"]["personal_relationship"] = self.thirdparty.relationship.data
            data["callback_type"] = CALLBACK_TYPES.CHECKER_THIRD_PARTY

            data["requires_action_at"] = process_selected_time(self.thirdparty.form.time)

        return data


class ConfirmationForm(Honeypot, BabelTranslationsFormMixin, Form):
    email = StringField(
        _(u"Receive this confirmation by email"),
        description=_(u"We will use this to send your reference number."),
        validators=[
            Length(max=255, message=_(u"Your address must be 255 characters or less")),
            EmailValidator(message=_(u"Enter a valid email address")),
            InputRequired(message=_(u"Tell us what email address to send to")),
        ],
    )
