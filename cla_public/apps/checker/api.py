from collections import OrderedDict
import logging
import urllib

from flask import current_app, session
from requests.exceptions import ConnectionError, Timeout
import slumber
from slumber.exceptions import SlumberBaseException

from cla_common.constants import ELIGIBILITY_STATES
from cla_public.apps.checker.constants import CATEGORIES
from cla_public.libs.api_proxy import on_timeout


log = logging.getLogger(__name__)


class ApiError(Exception):
    pass


def get_api_connection():
    return slumber.API(
        current_app.config['BACKEND_API']['url'],
        timeout=current_app.config['API_CLIENT_TIMEOUT']
    )


def money_interval(amount, interval='per_month'):
    return {
        'per_interval_value': amount,
        'interval_period': interval
    }


def initialise_eligibility_check(check):
    """Initialize the eligibility check API payload so that we will avoid
    getting 'unknown' eligibility all the time
    """

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
    set_(check, 'partner.income.earnings', money_interval(0))
    set_(check, 'partner.income.benefits', money_interval(0))
    set_(check, 'partner.income.tax_credits', money_interval(0))
    set_(check, 'partner.income.child_benefits', money_interval(0))
    set_(check, 'partner.income.other_income', money_interval(0))
    set_(check, 'partner.income.self_employment_drawings', money_interval(0))
    set_(check, 'partner.income.maintenance_received', money_interval(0))
    set_(check, 'partner.income.pension', money_interval(0))
    set_(check, 'partner.income.total', 0)
    set_(check, 'partner.income.self_employed', False)
    set_(check, 'partner.savings.credit_balance', 0)
    set_(check, 'partner.savings.investment_balance', 0)
    set_(check, 'partner.savings.total', 0)
    set_(check, 'partner.savings.asset_balance', 0)
    set_(check, 'partner.savings.bank_balance', 0)
    set_(check, 'partner.deductions.income_tax', money_interval(0))
    set_(check, 'partner.deductions.mortgage', money_interval(0))
    set_(check, 'partner.deductions.childcare', money_interval(0))
    set_(check, 'partner.deductions.rent', money_interval(0))
    set_(check, 'partner.deductions.maintenance', money_interval(0))
    set_(check, 'partner.deductions.national_insurance', money_interval(0))
    set_(check, 'partner.deductions.criminal_legalaid_contributions', 0)
    set_(check, 'dependants_young', 0)
    set_(check, 'dependants_old', 0)
    set_(check, 'on_passported_benefits', False)
    set_(check, 'on_nass_benefits', False)
    set_(check, 'specific_benefits', {})

    return check


def log_api_errors_to_sentry(fn):

    def wrapped(*args, **kwargs):
        sentry = getattr(current_app, 'sentry', None)
        try:
            fn(*args, **kwargs)
        except (ConnectionError, Timeout, SlumberBaseException) as e:
            if sentry:
                sentry.captureException()
            else:
                log.warning(
                    'Failed posting to API: {0}'.format(e))
            raise ApiError(e)

    return wrapped


@log_api_errors_to_sentry
def post_to_eligibility_check_api(form=None, payload={}):
    backend = get_api_connection()
    reference = session.checker.get('eligibility_check')
    payload = form.api_payload() if form else payload

    if reference is None:
        payload = initialise_eligibility_check(payload)
        response = backend.eligibility_check.post(payload)
        session.checker['eligibility_check'] = response['reference']
    else:
        backend.eligibility_check(reference).patch(payload)


@on_timeout(response=(ELIGIBILITY_STATES.UNKNOWN, []))
def post_to_is_eligible_api():
    backend = get_api_connection()
    reference = session.checker.get('eligibility_check')

    if reference:
        response = backend.eligibility_check(reference).is_eligible().post({})
        return response.get('is_eligible'), response.get('reasons')
    return None, None


def should_attach_eligibility_check():
    return 'eligibility_check' in session.checker


def attach_eligibility_check(payload):
    payload['eligibility_check'] = session.checker.get('eligibility_check')


@log_api_errors_to_sentry
def post_to_case_api(form):
    backend = get_api_connection()
    payload = form.api_payload()

    if should_attach_eligibility_check():
        attach_eligibility_check(payload)

    response = backend.case.post(payload)
    session.checker['case_ref'] = response['reference']


@on_timeout(response='[]')
def get_organisation_list(**kwargs):
    kwargs['page_size'] = 100
    key = 'organisation_list_%s' % urllib.urlencode(kwargs)
    organisation_list = current_app.cache.get(key)
    if not organisation_list:
        backend = get_api_connection()
        api_response = backend.organisation.get(**kwargs)
        organisation_list = api_response['results']

        one_year = 365 * 24 * 60 * 60
        current_app.cache.set(key, organisation_list, timeout=one_year)

    return organisation_list


def get_ordered_organisations_by_category(**kwargs):
    organisations = get_organisation_list(**kwargs)
    categories = OrderedDict((name, []) for field, name, description in CATEGORIES)
    for organisation in organisations:
        for cat in organisation['categories']:
            if cat['name'] in categories:
                categories[cat['name']].append(organisation)
                break
    return categories
