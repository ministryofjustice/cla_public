# -*- coding: utf-8 -*-
"CLA Public decorators"

import functools

from flask import current_app, render_template, request, session
import slumber


def override_session_vars():
    """Allow overriding session variables with URL parameters.
    No point validating since it's only for dev testing
    """
    for key, val in request.args.items():
        session[key] = val


def get_api_connection():
    return slumber.API(current_app.config['BACKEND_API']['url'])


def initialise_eligibility_check(check):
    """Initialize the eligibility check API payload so that we will avoid
    getting 'unknown' eligibility all the time
    """

    def money_interval(amount, interval='per_week'):
        return {
            'per_interval_value': amount,
            'interval_period': interval
        }

    def set_(dict_, path, value):
        key, _, rest = path.partition('.')
        if rest:
            dict_[key] = dict_.get(key, {})
            set_(dict_[key], rest, value)
        else:
            dict_[key] = dict_.get(key, value)

    set_(check, 'you.income.earnings', money_interval(0))
    set_(check, 'you.income.benefits', money_interval(0))
    set_(check, 'you.income.tax_credits', money_interval(0))
    set_(check, 'you.income.child_benefits', money_interval(0))
    set_(check, 'you.income.other_income', money_interval(0))
    set_(check, 'you.income.self_employment_drawings', money_interval(0))
    set_(check, 'you.income.maintenance_received', money_interval(0))
    set_(check, 'you.income.pension', money_interval(0))
    set_(check, 'you.income.total', 0)
    set_(check, 'you.income.self_employed', False)
    set_(check, 'you.savings.credit_balance', 0)
    set_(check, 'you.savings.investment_balance', 0)
    set_(check, 'you.savings.total', 0)
    set_(check, 'you.savings.asset_balance', 0)
    set_(check, 'you.savings.bank_balance', 0)
    set_(check, 'you.deductions.income_tax', money_interval(0))
    set_(check, 'you.deductions.mortgage', money_interval(0))
    set_(check, 'you.deductions.childcare', money_interval(0))
    set_(check, 'you.deductions.rent', money_interval(0))
    set_(check, 'you.deductions.maintenance', money_interval(0))
    set_(check, 'you.deductions.national_insurance', money_interval(0))
    set_(check, 'you.deductions.criminal_legalaid_contributions', 0)
    set_(check, 'dependants_young', 0)
    set_(check, 'dependants_old', 0)
    set_(check, 'on_passported_benefits', False)
    set_(check, 'on_nass_benefits', False)

    return check


def post_to_eligibility_check_api(form):
    backend = get_api_connection()
    reference = session.get('eligibility_check')
    payload = form.api_payload()

    if reference is None:
        payload = initialise_eligibility_check(payload)
        response = backend.eligibility_check.post(payload)
        session['eligibility_check'] = response['reference']
    else:
        backend.eligibility_check(reference).patch(payload)


def post_to_case_api(form):
    backend = get_api_connection()
    reference = session.get('eligibility_check')
    payload = form.api_payload()

    payload['eligibility_check'] = reference
    response = backend.case.post(payload)
    session['case_ref'] = response['reference']


def form_view(form_class, form_template):
    """Convenience decorator for form views"""

    def view(fn):

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):

            if current_app.config.get('DEBUG'):
                override_session_vars()

            form = form_class(request.form, session)
            if form.validate_on_submit():
                post_to_eligibility_check_api(form)
                return fn(session)

            return render_template(form_template, form=form)

        return wrapper

    return view
