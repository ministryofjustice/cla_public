# -*- coding: utf-8 -*-
"Checker views"

import logging
from cla_common.constants import ELIGIBILITY_STATES

from flask import abort, render_template, redirect, \
    session, url_for

from cla_public.apps.checker import checker
from cla_public.apps.checker.api import post_to_case_api, \
    post_to_eligibility_check_api, get_organisation_list
from cla_public.apps.callmeback.forms import CallMeBackForm
from cla_public.apps.checker.constants import RESULT_OPTIONS, CATEGORIES, \
    ORGANISATION_CATEGORY_MAPPING, NO_CALLBACK_CATEGORIES
from cla_public.apps.checker.decorators import form_view, \
    redirect_if_no_session, redirect_if_ineligible
from cla_public.apps.checker.forms import AboutYouForm, YourBenefitsForm, \
    ProblemForm, PropertiesForm, SavingsForm, TaxCreditsForm, income_form, \
    OutgoingsForm
from cla_public.libs.utils import override_locale


log = logging.getLogger(__name__)


def proceed(next_step, **kwargs):
    return redirect(url_for('.{0}'.format(next_step), **kwargs))


def outcome(outcome):
    return proceed('result', outcome=outcome)


@checker.after_request
def add_header(response):
    """
    Add no-cache headers
    """
    response.headers['Cache-Control'] = 'no-cache, no-store, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response


@checker.route('/problem', methods=['GET', 'POST'])
@form_view(ProblemForm, 'problem.html')
def problem(user):

    if user.needs_face_to_face:
        return outcome('face-to-face')

    return proceed('about')


@checker.route('/about', methods=['GET', 'POST'])
@redirect_if_no_session()
@form_view(AboutYouForm, 'about.html')
def about(user):

    next_step = 'income'

    if user.children_or_tax_credits:
        next_step = 'benefits_tax_credits'

    if user.has_savings_or_valuables:
        next_step = 'savings'

    if user.owns_property:
        next_step = 'property'

    if user.is_on_benefits:
        next_step = 'benefits'

    return proceed(next_step)


@checker.route('/benefits', methods=['GET', 'POST'])
@redirect_if_no_session()
@form_view(YourBenefitsForm, 'benefits.html')
def benefits(user):

    next_step = 'income'

    kwargs = {}
    if user.is_on_passported_benefits:
        kwargs['outcome'] = 'eligible'
        next_step = 'result'

    if user.children_or_tax_credits:
        kwargs = {}
        next_step = 'benefits_tax_credits'

    if user.has_savings_or_valuables:
        kwargs = {}
        next_step = 'savings'

    if user.owns_property:
        kwargs = {}
        next_step = 'property'

    return proceed(next_step, **kwargs)


@checker.route('/property', methods=['GET', 'POST'])
@redirect_if_no_session()
@form_view(PropertiesForm, 'property.html')
def property(user):

    next_step = 'income'

    kwargs = {}
    if user.is_on_passported_benefits:
        kwargs['outcome'] = 'eligible'
        next_step = 'result'

    if session.children_or_tax_credits:
        kwargs = {}
        next_step = 'benefits_tax_credits'

    if session.has_savings_or_valuables:
        kwargs = {}
        next_step = 'savings'

    return proceed(next_step, **kwargs)


@checker.route('/savings', methods=['GET', 'POST'])
@redirect_if_no_session()
@form_view(SavingsForm, 'savings.html')
def savings(user):
    next_step = 'income'

    kwargs = {}
    if user.is_on_passported_benefits:
        kwargs['outcome'] = 'eligible'
        next_step = 'result'

    if user.children_or_tax_credits:
        kwargs = {}
        next_step = 'benefits_tax_credits'

    return proceed(next_step, **kwargs)


@checker.route('/benefits-tax-credits', methods=['GET', 'POST'])
@redirect_if_no_session()
@form_view(TaxCreditsForm, 'benefits-tax-credits.html')
def benefits_tax_credits(user):
    next_step = 'income'

    kwargs = {}
    if user.is_on_passported_benefits:
        kwargs['outcome'] = 'eligible'
        next_step = 'result'

    return proceed(next_step, **kwargs)


@checker.route('/income', methods=['GET', 'POST'])
@redirect_if_no_session()
@form_view(income_form, 'income.html')
def income(user):
    return proceed('outgoings')


@checker.route('/outgoings', methods=['GET', 'POST'])
@redirect_if_no_session()
@form_view(OutgoingsForm, 'outgoings.html')
@redirect_if_ineligible()
def outgoings(user):
    return outcome('eligible')


@checker.route('/result/<outcome>', methods=['GET', 'POST'])
@redirect_if_no_session()
@redirect_if_ineligible()
def result(outcome):
    "Display the outcome of the means test"

    valid_outcomes = (result for (result, _) in RESULT_OPTIONS)
    if outcome not in valid_outcomes:
        abort(404)

    if session.category in NO_CALLBACK_CATEGORIES:
        session.clear()
        return render_template('result/eligible-no-callback.html')

    form = CallMeBackForm()
    if form.validate_on_submit():
        if form.extra_notes.data:
            session.add_note(
                u'User problem:\n{0}'.format(form.extra_notes.data))

        post_to_eligibility_check_api(session.notes_object())
        post_to_case_api(form)

        return redirect(url_for('.result', outcome='confirmation'))

    category_name = 'your issue'
    if session.category:
        category_name = session.category_name

    is_unknown = session.get('is_eligible') == ELIGIBILITY_STATES.UNKNOWN

    response = render_template(
        'result/%s.html' % outcome,
        form=form,
        category=session.category,
        category_name=category_name,
        eligibility_unknown=is_unknown)

    if outcome in ['confirmation', 'face-to-face']:
        session.clear()

    return response


@checker.route('/help-organisations/<category_name>', methods=['GET'])
def help_organisations(category_name):
    if session:
        session.clear()

    category_name = category_name.replace('-', ' ').capitalize()

    # force english as knowledge base languages are in english
    with override_locale('en'):
        requested = lambda slug, name, desc: name == category_name
        category, name, desc = next(iter(filter(requested, CATEGORIES)), None)

        if category is None:
            abort(404)

    category_name = ORGANISATION_CATEGORY_MAPPING.get(name, name)

    organisations = get_organisation_list(article_category__name=name)
    return render_template(
        'help-organisations.html',
        organisations=organisations,
        category=category)
