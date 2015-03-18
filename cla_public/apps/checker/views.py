# -*- coding: utf-8 -*-
"Checker views"

import logging

from flask import abort, render_template, redirect, session, url_for, views
from flask.ext.babel import lazy_gettext as _
from slumber.exceptions import SlumberBaseException
from requests.exceptions import ConnectionError, Timeout
from wtforms.validators import StopValidation

from cla_public.apps.checker import checker
from cla_public.apps.checker.api import get_organisation_list
from cla_public.apps.contact.forms import ContactForm
from cla_public.apps.checker.constants import CATEGORIES, \
    ORGANISATION_CATEGORY_MAPPING, NO_CALLBACK_CATEGORIES
from cla_public.apps.checker.forms import AboutYouForm, YourBenefitsForm, \
    ProblemForm, PropertiesForm, SavingsForm, TaxCreditsForm, OutgoingsForm, \
    IncomeForm, ReviewForm
from cla_public.apps.checker.means_test import MeansTest, MeansTestError
from cla_public.apps.checker.validators import IgnoreIf
from cla_public.apps.checker import honeypot
from cla_public.libs.utils import override_locale, log_to_sentry
from cla_public.libs.views import AllowSessionOverride, FormWizard, \
    FormWizardStep, RequiresSession


log = logging.getLogger(__name__)


@checker.app_context_processor
def get_selected_option():
    def option_label_fn(field, selected=None):
        options_dict = dict(field.choices)
        if not selected:
            selected = field.data
        return options_dict.get(selected)
    return {'selected_option': option_label_fn}


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
        means_test = session.get('means_test', MeansTest())
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


class CheckerStep(UpdatesMeansTest, FormWizardStep):

    def completed_fields(self):
        session_data = session.get(self.form_class.__name__, {})
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


class ReviewStep(FormWizardStep):

    def render(self, *args, **kwargs):
        steps = CheckerWizard('').relevant_steps[:-1]
        return render_template(self.template, steps=steps, form=self.form)


class CheckerWizard(AllowSessionOverride, FormWizard):

    steps = [
        ('problem', CheckerStep(ProblemForm, 'problem.html')),
        ('about', CheckerStep(AboutYouForm, 'about.html')),
        ('benefits', CheckerStep(YourBenefitsForm, 'benefits.html')),
        ('property', CheckerStep(PropertiesForm, 'property.html')),
        ('savings', CheckerStep(SavingsForm, 'savings.html')),
        ('benefits-tax-credits', CheckerStep(
            TaxCreditsForm, 'benefits-tax-credits.html')),
        ('income', CheckerStep(IncomeForm, 'income.html')),
        ('outgoings', CheckerStep(OutgoingsForm, 'outgoings.html')),
        ('review', ReviewStep(ReviewForm, 'review.html'))
    ]

    @property
    def relevant_steps(self):
        return filter(lambda s: not self.skip(s), self.steps)

    def complete(self):

        if session.needs_face_to_face:
            return redirect(url_for('.face-to-face'))

        if session.ineligible:
            return redirect(url_for(
                '.help_organisations',
                category_name=session.category_slug))

        return redirect(url_for('.eligible'))

    def skip(self, step):

        if session.needs_face_to_face:
            return True

        if step.name == 'review':
            return False

        if step.name not in ('problem', 'about', 'benefits') \
                and session.ineligible:
            return True

        if step.name == 'benefits':
            return not session.is_on_benefits

        if step.name == 'property':
            return not session.owns_property

        if step.name == 'savings':
            return not session.has_savings_or_valuables

        if step.name == 'benefits-tax-credits':
            return not session.children_or_tax_credits

        if session.is_on_passported_benefits \
                and step.name not in ('problem', 'about', 'benefits'):
            return True

        return False


checker.add_url_rule('/<step>', view_func=CheckerWizard.as_view('wizard'))


class FaceToFace(RequiresSession, views.MethodView, object):

    def get(self):
        if not session.category:
            session.category_name = 'your issue'

        response = render_template('result/face-to-face.html')
        session.clear()
        return response


checker.add_url_rule(
    '/result/face-to-face', view_func=FaceToFace.as_view('face-to-face'))


class Eligible(RequiresSession, views.MethodView, object):

    def get(self):
        if session.category in NO_CALLBACK_CATEGORIES:
            session.clear()
            return render_template('result/eligible-no-callback.html')

        return render_template('result/eligible.html', form=ContactForm())


checker.add_url_rule(
    '/result/eligible', view_func=Eligible.as_view('eligible'))


@checker.route('/help-organisations/<category_name>', methods=['GET'])
def help_organisations(category_name):
    if session:
        session.clear()

    category_name = category_name.replace('-', ' ').capitalize()

    # force english as knowledge base languages are in english
    with override_locale('en'):
        requested = lambda (slug, name, desc): name == category_name
        category, name, desc = next(
            iter(filter(requested, CATEGORIES)),
            (None, None, None))

        if category is None:
            abort(404)

        name = unicode(name)

        category_name = ORGANISATION_CATEGORY_MAPPING.get(name, name)
    trans_category_name = ORGANISATION_CATEGORY_MAPPING.get(name, name)

    organisations = get_organisation_list(article_category__name=category_name)
    return render_template(
        'help-organisations.html',
        organisations=organisations,
        category=category,
        category_name=trans_category_name)
