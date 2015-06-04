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
    NO_CALLBACK_CATEGORIES, LAALAA_PROVIDER_CATEGORIES_MAP
from cla_public.apps.checker.forms import AboutYouForm, YourBenefitsForm, \
    PropertiesForm, SavingsForm, TaxCreditsForm, OutgoingsForm, IncomeForm, \
    ReviewForm
from cla_public.apps.checker.means_test import MeansTest, MeansTestError
from cla_public.apps.checker.validators import IgnoreIf
from cla_public.apps.checker import honeypot
from cla_public.apps.checker import filters # Used in templates
from cla_public.libs.utils import override_locale, category_id_to_name
from cla_public.libs.views import AllowSessionOverride, FormWizard, \
    FormWizardStep, RequiresSession, ValidFormOnOptions, HasFormMixin
from cla_public.libs import laalaa


log = logging.getLogger(__name__)


@checker.after_request
def add_header(response):
    """
    Add no-cache headers
    """
    response.headers['Cache-Control'] = 'no-cache, no-store, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response


def handle_find_legal_adviser_form(form, args):
    data = {}
    category = ''
    page = 1

    if 'category' in args:
        category = LAALAA_PROVIDER_CATEGORIES_MAP.get(args['category'])

    if 'postcode' in args:
        if form.validate():
            if 'page' in args and args['page'].isdigit():
                page = args['page']
            data = laalaa.find(args['postcode'], category, page)
            if 'error' in data:
                form.postcode.errors.append(data['error'])
    return data


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
        ('property', CheckerStep(PropertiesForm, 'checker/property.html')),
        ('savings', CheckerStep(SavingsForm, 'checker/savings.html')),
        ('benefits-tax-credits', CheckerStep(
            TaxCreditsForm, 'checker/benefits-tax-credits.html')),
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
        if session.checker.needs_face_to_face:
            return redirect(
                url_for('.face-to-face', category=session.checker.category)
            )

        if session.checker.ineligible:
            session.store({
                'ineligible_reasons': session.checker.ineligible_reasons
            })
            return redirect(url_for(
                '.help_organisations',
                category_name=session.checker.category_slug))

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

        if step.name == 'property':
            return not session.checker.owns_property

        if step.name == 'savings':
            return not session.checker.has_savings_or_valuables

        if step.name == 'benefits-tax-credits':
            return not session.checker.children_or_tax_credits

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


class FaceToFace(views.MethodView, object):
    def get(self):
        form = FindLegalAdviserForm(request.args, csrf_enabled=False)
        data = handle_find_legal_adviser_form(form, request.args)

        session.store({'category': request.args.get('category') })

        category_name = None

        if session.stored['category']:
            category_name = category_id_to_name(session.stored['category'])

        session.clear_checker()

        response = render_template('checker/result/face-to-face.html',
            data=data, form=form, category_name=category_name)

        return response


checker.add_url_rule(
    '/result/face-to-face', view_func=FaceToFace.as_view('face-to-face'))


class EligibleNoCallBack(views.MethodView, object):

    def get(self):
        form = FindLegalAdviserForm(request.args, csrf_enabled=False)
        data = handle_find_legal_adviser_form(form, request.args)

        session.clear_checker()
        session.store({'category': request.args.get('category')})
        category_name = None
        if session.stored['category']:
            category_name = category_id_to_name(session.stored['category'])

        return render_template('checker/result/eligible-no-callback.html',
            data=data, form=form, category_name=category_name)

checker.add_url_rule(
    '/find-legal-adviser',
    view_func=EligibleNoCallBack.as_view('find-legal-adviser')
)


class Eligible(HasFormMixin, RequiresSession, views.MethodView, ValidFormOnOptions, object):

    form_class = ContactForm

    def get(self):
        steps = CheckerWizard('').relevant_steps[:-1]
        if session.checker.category in NO_CALLBACK_CATEGORIES:
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


class HelpOrganisations(views.MethodView):
    _template = 'help-organisations.html'

    def get_context(self, category_name):
        category_name = category_name.replace('-', ' ').capitalize()

        # force english as knowledge base languages are in english
        with override_locale('en'):
            category, name, desc = category_option_from_name(category_name)

            if category is None:
                abort(404)

            name = unicode(name)

            category_name = ORGANISATION_CATEGORY_MAPPING.get(name, name)
        trans_category_name = ORGANISATION_CATEGORY_MAPPING.get(name, name)

        ineligible_reasons = session.stored.get('ineligible_reasons', [])

        organisations = get_organisation_list(article_category__name=category_name)

        return {
            'organisations':organisations,
            'category': category,
            'category_name': trans_category_name,
            'ELIGIBILITY_REASONS': ELIGIBILITY_REASONS,
            'ineligible_reasons': ineligible_reasons
        }

    def clear_session(self):
        if session.checker:
            session.clear_checker()

    def get(self, category_name):
        self.clear_session()

        return render_template(
            self._template,
            **self.get_context(category_name)
        )


checker.add_url_rule(
    '/help-organisations/<category_name>',
    view_func=HelpOrganisations.as_view('help_organisations'),
    methods=['GET']
)
