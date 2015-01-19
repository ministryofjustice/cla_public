import datetime

from flask.json import JSONEncoder
from cla_common.constants import ELIGIBILITY_STATES
from flask.sessions import SecureCookieSession, SecureCookieSessionInterface


from cla_public.apps.checker.constants import F2F_CATEGORIES, NO, \
    PASSPORTED_BENEFITS, YES, CATEGORIES
from cla_public.apps.checker.utils import passported
from cla_public.libs.utils import override_locale


def namespace(ns):
    def prefix_key(item):
        key, value = item
        return ('{0}_{1}'.format(ns, key), value)
    return prefix_key


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

    @property
    def needs_face_to_face(self):
        return self.get('ProblemForm_categories') in F2F_CATEGORIES

    @property
    def need_more_info(self):
        """Show we need more information page instead of eligible"""
        if self.get('is_eligible', None) == ELIGIBILITY_STATES.UNKNOWN:
            return True
        properties = self.get('PropertiesForm_properties', [])
        if properties:
            return any(
                [p['in_dispute'] == YES or p['other_shareholders'] == YES for p in properties]
            )
        return False

    @property
    def category(self):
        return self.get('ProblemForm_categories')

    @property
    def category_name(self):
        return (name for field, name, description in CATEGORIES if field == self.category).next()

    @property
    def category_slug(self):
        # force english translation for slug
        with override_locale('en'):
            slug = self.category_name.lower().replace(' ', '-')
        return slug

    @property
    def has_savings(self):
        return self.get('AboutYouForm_have_savings', NO) == YES

    @property
    def has_valuables(self):
        return self.get('AboutYouForm_have_valuables', NO) == YES

    @property
    def has_savings_or_valuables(self):
        return self.has_savings or self.has_valuables

    @property
    def owns_property(self):
        return self.get('AboutYouForm_own_property', NO) == YES

    @property
    def is_on_benefits(self):
        return self.get('AboutYouForm_on_benefits', NO) == YES

    @property
    def is_on_passported_benefits(self):
        return passported(self.get('YourBenefitsForm_benefits', []))

    @property
    def has_tax_credits(self):
        has_children = self.get('AboutYouForm_have_children', NO) == YES
        is_carer = self.get('AboutYouForm_have_dependants', NO) == YES
        benefits = set(self.get('YourBenefitsForm_benefits', []))
        other_benefits = bool(benefits.difference(PASSPORTED_BENEFITS))
        return has_children or is_carer or other_benefits

    @property
    def has_children(self):
        return self.get('AboutYouForm_have_children', NO) == YES

    @property
    def has_dependants(self):
        return self.get('AboutYouForm_have_dependants', NO) == YES

    @property
    def children_or_tax_credits(self):
        return any([self.has_tax_credits,
                    self.has_children,
                    self.has_dependants])

    @property
    def has_partner(self):
        partner = self.get('AboutYouForm_have_partner', NO) == YES
        in_dispute = self.get('AboutYouForm_in_dispute', NO) == YES
        return partner and not in_dispute

    @property
    def is_employed(self):
        return self.get('AboutYouForm_is_employed', NO) == YES

    @property
    def is_self_employed(self):
        return self.get('AboutYouForm_is_self_employed', NO) == YES

    @property
    def partner_is_employed(self):
        return self.has_partner and self.get('AboutYouForm_partner_is_employed', NO) == YES

    @property
    def partner_is_self_employed(self):
        return self.has_partner and self.get('AboutYouForm_partner_is_self_employed', NO) == YES

    @property
    def aged_60_or_over(self):
        return self.get('AboutYouForm_aged_60_or_over', NO) == YES

    @property
    def callback_time(self):
        return self.get('CallMeBackForm_time')

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

    def update_form_data(self, form):
        classname = form.__class__.__name__
        form_data = map(namespace(classname), form.data.items())
        self.update(form_data)

    def clear_form_data(self, form):
        classname = form.__class__.__name__
        form_data = dict(map(namespace(classname), form.data.items()))
        for key in form_data.keys():
            if key in self:
                del self[key]

    def get_form_data(self, form_class_name):
        ns = '{0}_'.format(form_class_name)
        namespaced = lambda (key, val): key.startswith(ns)
        strip_ns = lambda (key, val): (key.replace(ns, ''), val)
        form_data = dict(map(strip_ns, filter(namespaced, self.items())))
        return form_data


class CheckerSessionInterface(SecureCookieSessionInterface):
    session_class = CheckerSession

    # Need to override the expires so that we can set the
    # session to expire 20 seconds from page close
    def get_expiration_time(self, app, session):
        if session.permanent:
            if session.expires_override:
                return session.expires_override

            return datetime.datetime.utcnow() + app.permanent_session_lifetime
