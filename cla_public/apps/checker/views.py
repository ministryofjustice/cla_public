# -*- coding: utf-8 -*-
"Checker views"

from flask import abort, render_template, redirect, session, url_for

import logging

from cla_public.apps.checker import checker
from cla_public.apps.checker.constants import RESULT_OPTIONS
from cla_public.apps.checker.decorators import form_view, get_api_connection
from cla_public.apps.checker.forms import AboutYouForm, YourBenefitsForm, \
    ProblemForm, PropertyForm, SavingsForm, TaxCreditsForm, IncomeAndTaxForm, \
    OutgoingsForm, ApplicationForm


log = logging.getLogger(__name__)


def proceed(next_step, **kwargs):
    return redirect(url_for('.{0}'.format(next_step), **kwargs))


def outcome(outcome):
    return proceed('result', outcome=outcome)


@checker.route('/problem', methods=['GET', 'POST'])
@form_view(ProblemForm, 'problem.html')
def problem(user):

    if user.needs_face_to_face:
        return outcome('face-to-face')

    return proceed('about')


@checker.route('/about', methods=['GET', 'POST'])
@form_view(AboutYouForm, 'about.html')
def about(user):

    next_step = 'income'

    if user.has_savings:
        next_step = 'savings'

    if user.owns_property:
        next_step = 'property'

    if user.is_on_benefits:
        next_step = 'benefits'

    return proceed(next_step)


@checker.route('/benefits', methods=['GET', 'POST'])
@form_view(YourBenefitsForm, 'benefits.html')
def benefits(user):

    if user.is_on_passported_benefits:
        return outcome('eligible')

    next_step = 'income'

    if user.has_tax_credits:
        next_step = 'benefits_tax_credits'

    if user.has_savings:
        next_step = 'savings'

    if user.owns_property:
        next_step = 'property'

    return proceed(next_step)


@checker.route('/property', methods=['GET', 'POST'])
@form_view(PropertyForm, 'property.html')
def property(user):

    next_step = 'income'

    if user.has_tax_credits:
        next_step = 'benefits_tax_credits'

    if user.has_savings:
        next_step = 'savings'

    return proceed(next_step)


@checker.route('/savings', methods=['GET', 'POST'])
@form_view(SavingsForm, 'savings.html')
def savings(user):
    next_step = 'income'

    if user.has_tax_credits:
        next_step = 'benefits_tax_credits'

    return proceed(next_step)


@checker.route('/benefits-tax-credits', methods=['GET', 'POST'])
@form_view(TaxCreditsForm, 'benefits-tax-credits.html')
def benefits_tax_credits(user):
    return proceed('income')


@checker.route('/income', methods=['GET', 'POST'])
@form_view(IncomeAndTaxForm, 'income.html')
def income(user):
    return proceed('outgoings')


@checker.route('/outgoings', methods=['GET', 'POST'])
@form_view(OutgoingsForm, 'outgoings.html')
def outgoings(user):
    return outcome('eligible')


@checker.route('/result/<outcome>', methods=['GET', 'POST'])
def result(outcome):
    "Display the outcome of the means test"

    valid_outcomes = (result for (result, _) in RESULT_OPTIONS)
    if outcome not in valid_outcomes:
        abort(404)

    reference = session.get('eligibility_check')
    is_eligible = 'unknown'
    if reference is not None:
        api = get_api_connection()
        import json
        session['means_test'] = json.dumps(api.eligibility_check(reference).get())
        response = api.eligibility_check(reference).is_eligible().post()
        is_eligible = response['is_eligible']

    form = ApplicationForm()
    if form.validate_on_submit():
        return redirect(url_for('.result', outcome='confirmation'))

    return render_template(
        'result/%s.html' % outcome, form=form, is_eligible=is_eligible)
