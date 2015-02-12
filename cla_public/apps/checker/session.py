import datetime

from flask.json import JSONEncoder
from flask.sessions import SecureCookieSession, SecureCookieSessionInterface
from requests.exceptions import ConnectionError, Timeout

from cla_common.constants import ELIGIBILITY_STATES
from cla_public.apps.checker.api import post_to_is_eligible_api
from cla_public.apps.checker.constants import F2F_CATEGORIES, NO, \
    PASSPORTED_BENEFITS, YES, CATEGORIES
from cla_public.apps.checker.utils import passported
from cla_public.libs.utils import override_locale


class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        if any([isinstance(obj, datetime.date),
                isinstance(obj, datetime.time),
                isinstance(obj, datetime.datetime)]):
            return obj.isoformat()
        return super(CustomJSONEncoder, self).default(obj)


class CheckerSession(SecureCookieSession):
    "Provides some convenience properties for inter-page logic"

    expires_override = None

    def __init__(self, *args, **kwargs):
        super(CheckerSession, self).__init__(*args, **kwargs)
        self._eligibility = None

    def __setitem__(self, *args, **kwargs):
        super(CheckerSession, self).__setitem__(*args, **kwargs)
        self._eligibility = None

    def field(self, form_name, field_name, default=None):
        return self.get(form_name, {}).get(field_name, default)

    @property
    def needs_face_to_face(self):
        return self.field('ProblemForm', 'categories') in F2F_CATEGORIES

    @property
    def ineligible(self):
        return self.eligibility == ELIGIBILITY_STATES.NO

    @property
    def eligibility(self):
        if self._eligibility is None:
            try:
                self._eligibility = post_to_is_eligible_api()
            except (ConnectionError, Timeout):
                self._eligibility = ELIGIBILITY_STATES.UNKNOWN
        return self._eligibility

    @property
    def need_more_info(self):
        """Show we need more information page instead of eligible"""
        if self.eligibility == ELIGIBILITY_STATES.UNKNOWN:
            return True
        properties = self.field('PropertiesForm', 'properties')
        if properties:
            return any(
                [p['in_dispute'] == YES or p['other_shareholders'] == YES
                 for p in properties]
            )
        return False

    @property
    def category(self):
        return self.field('ProblemForm', 'categories')

    @property
    def category_name(self):
        selected_name = lambda (slug, name, _): slug == self.category and name
        selected = filter(None, map(selected_name, CATEGORIES))
        return selected[0] if selected else None

    @property
    def category_slug(self):
        # force english translation for slug
        cat_name = self.category_name
        if cat_name:
            with override_locale('en'):
                slug = cat_name.lower().replace(' ', '-')
            return slug

    def is_yes(self, form, field):
        return self.field(form, field, NO) == YES

    @property
    def has_savings(self):
        return self.is_yes('AboutYouForm', 'have_savings')

    @property
    def has_valuables(self):
        return self.is_yes('AboutYouForm', 'have_valuables')

    @property
    def has_savings_or_valuables(self):
        return self.has_savings or self.has_valuables

    @property
    def owns_property(self):
        return self.is_yes('AboutYouForm', 'own_property')

    @property
    def is_on_benefits(self):
        return self.is_yes('AboutYouForm', 'on_benefits')

    @property
    def is_on_passported_benefits(self):
        return passported(self.field('YourBenefitsForm', 'benefits', []))

    @property
    def has_tax_credits(self):
        has_children = self.is_yes('AboutYouForm', 'have_children')
        is_carer = self.is_yes('AboutYouForm', 'have_dependants')
        benefits = set(self.field('YourBenefitsForm', 'benefits', []))
        other_benefits = bool(benefits.difference(PASSPORTED_BENEFITS))
        return has_children or is_carer or other_benefits

    @property
    def has_children(self):
        return self.is_yes('AboutYouForm', 'have_children')

    @property
    def has_dependants(self):
        return self.is_yes('AboutYouForm', 'have_dependants')

    @property
    def children_or_tax_credits(self):
        return any([self.has_tax_credits,
                    self.has_children,
                    self.has_dependants])

    @property
    def has_partner(self):
        partner = self.is_yes('AboutYouForm', 'have_partner')
        in_dispute = self.is_yes('AboutYouForm', 'in_dispute')
        return partner and not in_dispute

    @property
    def is_employed(self):
        return self.is_yes('AboutYouForm', 'is_employed')

    @property
    def is_self_employed(self):
        return self.is_yes('AboutYouForm', 'is_self_employed')

    @property
    def partner_is_employed(self):
        return self.has_partner and \
            self.is_yes('AboutYouForm', 'partner_is_employed')

    @property
    def partner_is_self_employed(self):
        return self.has_partner and \
            self.is_yes('AboutYouForm', 'partner_is_self_employed')

    @property
    def aged_60_or_over(self):
        return self.is_yes('AboutYouForm', 'aged_60_or_over')

    @property
    def callback_time(self):
        return self.field('CallMeBackForm', 'time')

    def add_note(self, note):
        notes = self.get('notes', [])
        notes.append(note)
        self['notes'] = notes

    def notes_object(self):
        session = self

        class Notes(object):
            def api_payload(self):
                return {'notes': '\n\n'.join(session.get('notes', []))}

        return Notes()

    @property
    def contact_preference(self):
        return self.field('CallMeBackForm', 'callback_requested')


class CheckerSessionInterface(SecureCookieSessionInterface):
    session_class = CheckerSession

    # Need to override the expires so that we can set the
    # session to expire 20 seconds from page close
    def get_expiration_time(self, app, session):
        if session.permanent:
            if session.expires_override:
                return session.expires_override

            return datetime.datetime.utcnow() + app.permanent_session_lifetime
