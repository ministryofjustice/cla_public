# -*- coding: utf-8 -*-
"Checker views"

import logging

from flask import abort, render_template, redirect, session, url_for, views
from flask.ext.babel import lazy_gettext as _, lazy_pgettext
from requests.exceptions import ConnectionError, Timeout

from cla_common.constants import ELIGIBILITY_STATES
from cla_public.apps.checker import checker
from cla_public.apps.checker.api import post_to_case_api, \
    post_to_eligibility_check_api, get_organisation_list, \
    post_to_is_eligible_api, ineligible
from cla_public.apps.callmeback.forms import CallMeBackForm
from cla_public.apps.checker.constants import RESULT_OPTIONS, CATEGORIES, \
    ORGANISATION_CATEGORY_MAPPING, NO_CALLBACK_CATEGORIES
from cla_public.apps.checker.decorators import redirect_if_no_session, \
    redirect_if_ineligible
from cla_public.apps.checker.forms import AboutYouForm, YourBenefitsForm, \
    ProblemForm, PropertiesForm, SavingsForm, TaxCreditsForm, OutgoingsForm, \
    IncomeForm
from cla_public.libs.utils import override_locale
from cla_public.libs.views import AllowSessionOverride, FormWizard, \
    FormWizardStep, RequiresSession


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
        try:
            post_to_eligibility_check_api(self.form)
        except (ConnectionError, Timeout):
            self.form.errors['timeout'] = _(
                u'Server did not respond, please try again')
            return self.get(step=self.name)
        return super(UpdatesMeansTest, self).on_valid_submit()


class CheckerStep(UpdatesMeansTest, FormWizardStep):

    @property
    def form(self):
        return self.wizard.form

    def get(self, **kwargs):
        return self.wizard.get(**kwargs)

    def on_valid_submit(self):

        if session.needs_face_to_face:
            return redirect(url_for('.face-to-face'))

        if session.is_on_passported_benefits:
            return redirect(url_for('.eligible'))

        if self.name == 'outgoings':
            return redirect(url_for('.eligible'))

        return super(CheckerStep, self).on_valid_submit()


class OutgoingsStep(CheckerStep, FormWizardStep):

    def on_valid_submit(self):
        redirect_if_ineligible()
        return super(OutgoingsStep, self).on_valid_submit()


class CheckerWizard(FormWizard):

    steps = [
        ('problem', CheckerStep(ProblemForm, 'problem.html')),
        ('about', CheckerStep(AboutYouForm, 'about.html')),
        ('benefits', CheckerStep(YourBenefitsForm, 'benefits.html')),
        ('property', CheckerStep(PropertiesForm, 'property.html')),
        ('savings', CheckerStep(SavingsForm, 'savings.html')),
        ('benefits_tax_credits', CheckerStep(
            TaxCreditsForm, 'benefits-tax-credits.html')),
        ('income', CheckerStep(IncomeForm, 'income.html')),
        ('outgoings', OutgoingsStep(OutgoingsForm, 'outgoings.html'))
    ]

    def skip(self, step):
        user = session

        if step.name == 'benefits':
            return not user.is_on_benefits

        if step.name == 'property':
            return not user.owns_property

        if step.name == 'savings':
            return not user.has_savings_or_valuables

        if step.name == 'benefits_tax_credits':
            return not user.children_or_tax_credits

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
    '/result/face-to-face', view_func=FaceToFace.as_view('face_to_face'))


class Eligible(RequiresSession, views.MethodView, object):

    def get(self):
        if session.category in NO_CALLBACK_CATEGORIES:
            session.clear()
            return render_template('result/eligible-no-callback.html')

        return redirect(url_for('callmeback.request_callback'))


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

        category_name = ORGANISATION_CATEGORY_MAPPING.get(unicode(name), unicode(name))
    trans_category_name = ORGANISATION_CATEGORY_MAPPING.get(unicode(name), unicode(name))

    organisations = get_organisation_list(article_category__name=category_name)
    return render_template(
        'help-organisations.html',
        organisations=organisations,
        category=category,
        category_name=trans_category_name)
