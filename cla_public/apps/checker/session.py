from collections import OrderedDict
import hashlib
import uuid
from base64 import b64encode, b64decode
from datetime import datetime, date, time
from speaklater import _LazyString
from werkzeug.http import http_date, parse_date
from flask import Markup, json
from flask._compat import iteritems, text_type
from flask.debughelpers import UnexpectedUnicodeError
from flask import current_app, flash
from flask.json import JSONEncoder
from flask.sessions import SecureCookieSession, SecureCookieSessionInterface, SessionMixin, TaggedJSONSerializer

from cla_common.constants import ELIGIBILITY_STATES
from cla_public.apps.checker.api import post_to_is_eligible_api, ApiError
from cla_public.apps.checker.constants import (
    F2F_CATEGORIES,
    NO,
    PASSPORTED_BENEFITS,
    YES,
    END_SERVICE_FLASH_MESSAGE,
    CONTACT_PREFERENCE,
)
from cla_public.apps.checker.means_test import MeansTest
from cla_public.apps.checker.utils import passported
from cla_public.libs.utils import override_locale, category_id_to_name


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if any([isinstance(obj, date), isinstance(obj, time), isinstance(obj, datetime)]):
            return obj.isoformat()
        elif isinstance(obj, _LazyString):
            return unicode(obj)
        return super(CustomJSONEncoder, self).default(obj)


class CheckerSessionObject(dict):
    "Provides some convenience properties for inter-page logic"
    _eligibility = None

    def __init__(self, *args, **kwargs):
        super(CheckerSessionObject, self).__init__(*args, **kwargs)
        self._eligibility = None
        self._reasons = None

    def __setitem__(self, *args, **kwargs):
        super(CheckerSessionObject, self).__setitem__(*args, **kwargs)
        self._eligibility = None
        self._reasons = None

    def field(self, form_name, field_name, default=None):
        return self.get(form_name, {}).get(field_name, default)

    # TODO: Check if redundant because scope diagnosis manages F2F redirects
    @property
    def needs_face_to_face(self):
        return self.category in F2F_CATEGORIES

    @property
    def ineligible_reasons(self):
        return self._reasons or []

    @property
    def ineligible(self):
        return self.eligibility == ELIGIBILITY_STATES.NO

    @property
    def eligibility(self):
        if self._eligibility is None:
            try:
                self._eligibility, self._reasons = post_to_is_eligible_api()
            except ApiError:
                self._eligibility = ELIGIBILITY_STATES.UNKNOWN
        return self._eligibility

    @property
    def need_more_info(self):
        """Show we need more information page instead of eligible"""
        if self.eligibility == ELIGIBILITY_STATES.UNKNOWN:
            return True
        properties = self.field("PropertiesForm", "properties")
        if properties:
            return any([p["in_dispute"] == YES or p["other_shareholders"] == YES for p in properties])
        return False

    @property
    def category(self):
        return self.get("category")

    @property
    def category_name(self):
        return category_id_to_name(self.category)

    @property
    def category_slug(self):
        # force english translation for slug
        cat_name = self.category_name
        if cat_name:
            with override_locale("en"):
                slug = cat_name.lower().replace(" ", "-")
            return slug

    def is_yes(self, form, field):
        return self.field(form, field, NO) == YES

    @property
    def has_savings(self):
        return self.is_yes("AboutYouForm", "have_savings")

    @property
    def has_valuables(self):
        return self.is_yes("AboutYouForm", "have_valuables")

    @property
    def has_savings_or_valuables(self):
        return self.has_savings or self.has_valuables

    @property
    def owns_property(self):
        return self.is_yes("AboutYouForm", "own_property")

    @property
    def is_on_benefits(self):
        return self.is_yes("AboutYouForm", "on_benefits")

    @property
    def is_on_passported_benefits(self):
        return self.is_on_benefits and passported(self.field("YourBenefitsForm", "benefits", []))

    @property
    def is_on_other_benefits(self):
        benefits = set(self.field("YourBenefitsForm", "benefits", []))
        other_benefits = benefits.difference(PASSPORTED_BENEFITS).difference({"child_benefit"})
        return self.is_on_benefits and bool(other_benefits)

    @property
    def has_children(self):
        return self.is_yes("AboutYouForm", "have_children")

    @property
    def has_dependants(self):
        return self.is_yes("AboutYouForm", "have_dependants")

    @property
    def has_partner(self):
        partner = self.is_yes("AboutYouForm", "have_partner")
        in_dispute = self.is_yes("AboutYouForm", "in_dispute")
        return partner and not in_dispute

    @property
    def is_employed(self):
        return self.is_yes("AboutYouForm", "is_employed")

    @property
    def is_self_employed(self):
        return self.is_yes("AboutYouForm", "is_self_employed")

    @property
    def partner_is_employed(self):
        return self.has_partner and self.is_yes("AboutYouForm", "partner_is_employed")

    @property
    def partner_is_self_employed(self):
        return self.has_partner and self.is_yes("AboutYouForm", "partner_is_self_employed")

    @property
    def aged_60_or_over(self):
        return self.is_yes("AboutYouForm", "aged_60_or_over")

    @property
    def callback_time(self):
        if self.contact_type == "thirdparty":
            return self.field("ContactForm", "thirdparty", {}).get("time", None)
        return self.field("ContactForm", "callback", {}).get("time", None)

    def add_note(self, key, note):
        notes = self.get("notes", OrderedDict())
        notes[key] = note
        self["notes"] = notes

    def notes_object(self):
        session = self

        def format_note(note_item):
            return u"{key}:\n{note}".format(key=note_item[0], note=note_item[1])

        class Notes(object):
            def api_payload(self):
                return {"notes": u"\n\n".join(map(format_note, session.get("notes", {}).items()))}

        return Notes()

    @property
    def contact_type(self):
        return self.get("ContactForm", {}).get("contact_type")


class CheckerSession(SecureCookieSession, SessionMixin):
    "Provides some convenience properties for inter-page logic"

    _key = "checker"
    _stored_key = "stored"
    expires_override = None

    def __init__(self, *args, **kwargs):
        self.checker = CheckerSessionObject()
        self.stored = {}
        super(CheckerSession, self).__init__(*args, **kwargs)

    @property
    def checker(self):
        return self[self._key]

    @checker.setter
    def checker(self, value):
        checker = CheckerSessionObject()
        checker.update(value)
        self[self._key] = value

    @property
    def stored(self):
        return self[self._stored_key]

    @stored.setter
    def stored(self, value):
        assert isinstance(value, dict)
        self[self._stored_key] = value

    @property
    def is_current(self):
        return not self.get("is_expired", False) and self.checker

    def store_checker_details(self):
        outcome = self.stored.get("outcome", "incomplete")
        self.stored = {
            "case_ref": self.checker.get("case_ref"),
            "callback_time": self.checker.callback_time,
            "callback_requested": self.checker.contact_type
            in [type[0] for type in CONTACT_PREFERENCE if type[0] != "call"],
            "contact_type": self.checker.contact_type,
            "category": self.checker.category,
            "eligibility": self.checker.eligibility,
            "outcome": outcome,
            "adaptations": [k for k, v in self.checker.get("ContactForm", {}).get("adaptations", {}).items() if v],
        }

    def store(self, values_dict):
        self.stored.update(values_dict)

    def clear_checker(self):
        if self.checker:
            flash(unicode(END_SERVICE_FLASH_MESSAGE))
        self.checker = CheckerSessionObject()

    def clear(self):
        if current_app.config["CLEAR_SESSION"]:
            super(CheckerSession, self).clear()
            self.checker = CheckerSessionObject()

class Tag:
    def __init__(self):
        self.instances = [
            {
                'value': CheckerSessionObject,
                'method': self.isACheckSessionObjectisAC
            },
            {
                'value': MeansTest,
                'method': self.isAMeansTestObject
            },
            {
                'value': tuple,
                'method': self.isATupleObject
            },
            {
                'value': uuid.UUID,
                'method': self.isAUUIDObject
            },
            {
                'value': bytes,
                'method': self.isAByteObject
            },
            {
                'value': "__html__",
                'method': self.isCallable
            },
            {
                'value': list,
                'method': self.isAListObject
            },
            {
                'value': datetime,
                'method': self.isADatetimeObject
            },
            {
                'value': dict,
                'method': self.isADictObject
            },
            {
                'value': str,
                'method': self.isAString
            }
        ]

    def isACheckSessionObject(self, value):
        return {" ch": dict((k, self.checkTag(v)) for k, v in iteritems(value))}

    def isAMeansTestObject(self, value):
        return {" mt": dict((k, self.checkTag(v)) for k, v in iteritems(value))}

    def isATupleObject(self, value):
        return {" t": [self.checkTag(x) for x in value]}

    def isAUUIDObject(self, value):
        return {" u": value.hex}

    def isAByteObject(self, value):
        return {" b": b64encode(value).decode("ascii")}

    def isCallable(self, value):
        return {" m": text_type(value.__html__())}

    def isAListObject(self, value):
        return [self.checkTag(x) for x in value]

    def isADatetimeObject(self, value):
        return {" d": http_date(value)}

    def isADictObject(self, value):
        return dict((k, self.checkTag(v)) for k, v in iteritems(value))

    def isAString(self, value):
        try:
            return text_type(value)
        except UnicodeError:
            raise UnexpectedUnicodeError(
                u"A byte string with "
                u"non-ASCII data was passed to the session system "
                u"which can only store unicode strings.  Consider "
                u"base64 encoding your string (String was %r)" % value
            )

    def checkTag(self, value):
        for instance in self.instaces:
            if(instance.value == "__html__"):
                if(callable(getattr(value, "__html__", None))):
                    return instance.method(value)
            elif(isinstance(value, instance.value)):
                return instance.method(value)
        return value


class CheckerTaggedJSONSerializer(TaggedJSONSerializer):
    def dumps(self, value):
        tag = Tag()
        _tag = tag.checkTag
        return json.dumps(_tag(value), separators=(",", ":"))

    def loads(self, value):
        def object_hook(obj):
            if len(obj) != 1:
                return obj
            the_key, the_value = next(iteritems(obj))
            if the_key == " t":
                return tuple(the_value)
            elif the_key == " u":
                return uuid.UUID(the_value)
            elif the_key == " b":
                return b64decode(the_value)
            elif the_key == " m":
                return Markup(the_value)
            elif the_key == " d":
                return parse_date(the_value)
            elif the_key == " ch":
                c = CheckerSessionObject()
                c.update(the_value)
                return c
            elif the_key == " mt":
                m = MeansTest()
                m.update(the_value)
                return m
            return obj

        return json.loads(value, object_hook=object_hook)


checker_session_serializer = CheckerTaggedJSONSerializer()


class CheckerSessionInterface(SecureCookieSessionInterface):
    digest_method = staticmethod(hashlib.sha256)
    session_class = CheckerSession
    serializer = checker_session_serializer

    # Need to override the expires so that we can set the
    # session to expire 20 seconds from page close
    def get_expiration_time(self, app, session):
        if session.permanent:
            if session.expires_override:
                return session.expires_override

            return datetime.utcnow() + app.permanent_session_lifetime
