# -*- coding: utf-8 -*-
"Checker views"
import logging
from cla_common.constants import ELIGIBILITY_REASONS

from flask import abort, render_template, redirect, session, url_for, views, \
    request

from flask.ext.babel import lazy_gettext as _
from wtforms.validators import StopValidation
from cla_public.apps.checker import checker
from cla_public.apps.checker.api import get_organisation_list
from cla_public.apps.checker.forms import FindLegalAdviserForm
from cla_public.apps.checker.utils import category_option_from_name
from cla_public.apps.contact.forms import ContactForm
from cla_public.apps.checker.constants import ORGANISATION_CATEGORY_MAPPING, \
    NO_CALLBACK_CATEGORIES, LAALAA_PROVIDER_CATEGORIES_MAP, CATEGORIES
from cla_public.apps.checker.forms import AboutYouForm, YourBenefitsForm, \
    PropertiesForm, SavingsForm, OutgoingsForm, IncomeForm, \
    ReviewForm, AdditionalBenefitsForm
from cla_public.apps.checker.means_test import MeansTest, MeansTestError
from cla_public.apps.checker.validators import IgnoreIf
from cla_public.apps.checker import filters  # Used in templates
from cla_public.libs.utils import override_locale, category_id_to_name
from cla_public.libs.views import AllowSessionOverride, FormWizard, \
    FormWizardStep, RequiresSession, ValidFormOnOptions, HasFormMixin
from cla_public.libs import laalaa, honeypot

from .cait_intervention import get_cait_params

log = logging.getLogger(__name__)


@checker.after_request
def add_header(response):
    """
    Add no-cache headers
    """
    response.headers['Cache-Control'] = 'no-cache, no-store, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response


class UpdatesMeansTest(object):

    def on_valid_submit(self):
        means_test = session.checker.get('means_test', MeansTest())
        means_test.update_from_session()
        try:
            means_test.save()
        except MeansTestError:
            self.form.errors['timeout'] = _(
                u'There was an error submitting your data. '
                u'Please check and try again.')
            return self.get(step=self.name)
        else:
            return super(UpdatesMeansTest, self).on_valid_submit()


def is_null(field):

    if field.data is None:
        return True

    if hasattr(field, '_money_interval_field'):
        if field.data['per_interval_value'] is None:
            return True

    if isinstance(field.data, list):
        if len(field.data) == 0:
            return True

    if hasattr(field, 'form'):
        if all(map(is_null, field.form._fields.values())):
            return True

    return False


class CheckerStep(ValidFormOnOptions, UpdatesMeansTest, FormWizardStep):

    def completed_fields(self):
        session_data = session.checker.get(self.form_class.__name__, {})
        form = self.form_class(**session_data)

        def user_completed(field):
            name, field = field
            if name in ['csrf_token', honeypot.FIELD_NAME]:
                return False

            def should_ignore(field):
                ignore_validators = filter(
                    lambda v: isinstance(v, IgnoreIf),
                    field.validators)

                def triggered(v):
                    try:
                        v(form, field)
                    except StopValidation:
                        return True
                    return False

                return any(map(triggered, ignore_validators))

            if should_ignore(field):
                return False

            return not is_null(field)

        fields = filter(user_completed, form._fields.items())
        fields = map(lambda (name, field): (field), fields)
        return fields

    @property
    def is_completed(self):
        return session.checker.get(
            self.form_class.__name__,
            {}
        ).get('is_completed', False)

    @property
    def is_current(self):
        if request.view_args:
            return self.name == request.view_args['step']
        else:
            return False

    @property
    def count(self):
        steps = CheckerWizard('').relevant_steps[:-1]
        for index, item in enumerate(steps):
            if item.name == self.name:
                return index + 1
        return None

    def render(self, *args, **kwargs):
        steps = CheckerWizard('').relevant_steps[:-1]
        current_step = None
        if self.count:
            current_step = steps[self.count-1]

        return render_template(
            self.template,
            steps=steps,
            current_step=current_step,
            form=self.form
        )


class ReviewStep(CheckerStep):
    @property
    def count(self):
        steps = CheckerWizard('').relevant_steps[:-1]
        return len(steps) + 1

    def render(self, *args, **kwargs):
        steps = CheckerWizard('').relevant_steps[:-1]
        current_step = self
        return render_template(
            self.template,
            steps=steps,
            current_step=current_step,
            form=self.form
        )


class CheckerWizard(AllowSessionOverride, FormWizard):

    steps = [
        ('about', CheckerStep(AboutYouForm, 'checker/about.html')),
        ('benefits', CheckerStep(YourBenefitsForm, 'checker/benefits.html')),
        ('additional-benefits', CheckerStep(
            AdditionalBenefitsForm, 'checker/additional-benefits.html')),
        ('property', CheckerStep(PropertiesForm, 'checker/property.html')),
        ('savings', CheckerStep(SavingsForm, 'checker/savings.html')),
        ('income', CheckerStep(IncomeForm, 'checker/income.html')),
        ('outgoings', CheckerStep(OutgoingsForm, 'checker/outgoings.html')),
        ('review', ReviewStep(ReviewForm, 'checker/review.html'))
    ]

    @property
    def relevant_steps(self):
        return filter(lambda s: not self.skip(s), self.steps)

    @property
    def review_steps(self):
        return filter(lambda s: not self.skip_on_review(s), self.steps)

    def complete(self):
        # TODO: Is this still used now that scope diagnosis is taking care of F2F redirects for certain categories?
        if session.checker.needs_face_to_face:
            return redirect(
                url_for('.face-to-face', category=session.checker.category)
            )

        if session.checker.ineligible:
            session.store({
                'ineligible_reasons': session.checker.ineligible_reasons,
                'outcome': 'referred/help-organisations/means'
            })
            return redirect(url_for(
                '.help_organisations',
                category_name=session.checker.category_slug))

        if session.checker.need_more_info:
            session.store({'outcome': 'provisional'})
            return redirect(url_for('.provisional'))

        session.store({'outcome': 'eligible'})
        return redirect(url_for('.eligible'))

    def skip(self, step, for_review_page=False):

        if session.checker.needs_face_to_face:
            return True

        if step.name == 'review':
            return False

        if not for_review_page \
                and step.name not in ('about', 'benefits') \
                and session.checker.ineligible:
            return True

        if step.name == 'benefits':
            return not session.checker.is_on_benefits

        if step.name == 'additional-benefits':
            return not session.checker.is_on_other_benefits

        if step.name == 'property':
            return not session.checker.owns_property

        if step.name == 'savings':
            return not session.checker.has_savings_or_valuables

        if session.checker.is_on_passported_benefits \
                and step.name not in ('about', 'benefits'):
            return True

        return False

    def skip_on_review(self, step):
        if self.skip(step, for_review_page=True) or not step.is_completed:
            return True
        return False


checker.add_url_rule('/<step>', view_func=CheckerWizard.as_view('wizard'),
                     methods=('GET', 'POST', 'OPTIONS'))


class LaaLaaView(views.MethodView):
    """
    Find a legal adviser view
    Requires no session so is directly accessible
    """
    template = 'laalaa.html'
    view_clears_session = False

    @classmethod
    def handle_find_legal_adviser_form(cls, form, args):
        data = {}
        category = ''
        page = 1

        if 'category' in args:
            category = LAALAA_PROVIDER_CATEGORIES_MAP.get(args['category'])

        if 'postcode' in args:
            if form.validate():
                if 'page' in args and args['page'].isdigit():
                    page = args['page']
                try:
                    data = laalaa.find(args['postcode'], category, page)
                    if 'error' in data:
                        form.postcode.errors.append(data['error'])
                except laalaa.LaaLaaError:
                    form.postcode.errors.append(u"%s %s" % (
                        _('Error looking up legal advisers.'),
                        _('Please try again later.')
                    ))
        data['current_page'] = page
        return data

    def get(self):
        if self.view_clears_session:
            session.clear_checker()
        category = request.args.get('category')
        if category == 'other':
            category = ''
        category_name = None
        if category:
            category_name = category_id_to_name(category)

        return self.render(category=category, category_name=category_name)

    def render(self, category, category_name, extra_context={}):
        form = FindLegalAdviserForm(request.args, csrf_enabled=False)
        data = self.handle_find_legal_adviser_form(form, request.args)

        return render_template(self.template, category=category,
                               category_name=category_name,
                               data=data, form=form, **extra_context)


checker.add_url_rule(
    '/find-a-legal-adviser',
    view_func=LaaLaaView.as_view('laalaa')
)


class FaceToFace(LaaLaaView):
    template = 'checker/result/face-to-face.html'
    view_clears_session = True


checker.add_url_rule(
    '/scope/refer/legal-adviser',
    view_func=FaceToFace.as_view('face-to-face'))


class EligibleFaceToFace(LaaLaaView):
    template = 'checker/result/eligible-f2f.html'
    view_clears_session = True


checker.add_url_rule(
    '/result/refer/legal-adviser',
    view_func=EligibleFaceToFace.as_view('find-legal-adviser')
)


class Eligible(HasFormMixin, RequiresSession, views.MethodView, ValidFormOnOptions, object):

    form_class = ContactForm

    def get(self):
        steps = CheckerWizard('').relevant_steps[:-1]
        if session.checker.category in NO_CALLBACK_CATEGORIES:
            session.store({'outcome': 'referred/f2f/means'})
            return redirect(
                url_for('.find-legal-adviser', category=session.checker.category)
            )

        current_step = {
            'count': len(steps) + 1,
            'is_current': True,
            'is_completed': False
        }

        return render_template(
            'checker/result/eligible.html',
            current_step=current_step,
            steps=steps,
            form=self.form
        )


checker.add_url_rule(
    '/result/eligible',
    view_func=Eligible.as_view('eligible'),
    methods=('GET', 'POST', 'OPTIONS')
)

checker.add_url_rule(
    '/result/provisional',
    view_func=Eligible.as_view('provisional'),
    methods=('GET', 'POST', 'OPTIONS')
)


class HelpOrganisations(views.MethodView):
    _template = 'checker/result/ineligible.html'

    def get_context(self, category_name, checker):
        category_name = category_name.replace('-', ' ').capitalize()

        # force english as knowledge base languages are in english
        with override_locale('en'):
            category, name, desc = category_option_from_name(category_name)

            if category is None:
                abort(404)

            name = unicode(name)

            category_name = ORGANISATION_CATEGORY_MAPPING.get(name, name)
        trans_category_name = next(c[1] for c in CATEGORIES if c[0] == category)

        ineligible_reasons = session.stored.get('ineligible_reasons', [])

        organisations = get_organisation_list(article_category__name=category_name)

        params = {
            'organisations': organisations,
            'category': category,
            'category_name': trans_category_name,
            'ELIGIBILITY_REASONS': ELIGIBILITY_REASONS,
            'ineligible_reasons': ineligible_reasons,
            'truncate': 5
        }
        params = get_cait_params(params, category_name, organisations, checker)
        return params

    def clear_session(self):
        if session.checker:
            session.clear_checker()

    def get(self, category_name):
        checker = session.checker
        self.clear_session()

        return render_template(
            self._template,
            **self.get_context(category_name, checker)
        )


checker.add_url_rule(
    '/result/refer/<category_name>',
    view_func=HelpOrganisations.as_view('help_organisations'),
    methods=['GET']
)


@checker.route('/legal-aid-available')
def interstitial():
    """
    Interstitial page after passing scope test
    """
    if not session or not session.is_current or not session.checker.category:
        return redirect(url_for('base.session_expired'))

    category = session.checker.category
    category_name = session.checker.category_name
    with override_locale('en'):
        category_name_english = unicode(session.checker.category_name)

    organisations = get_organisation_list(article_category__name=category_name_english)
    show_laalaa = category in ['family', 'housing']

    context = {
        'category': category,
        'category_name': category_name,
        'organisations': organisations,
        'show_laalaa': show_laalaa,
    }
    return render_template('interstitial.html', **context)
