from collections import OrderedDict
import logging
import urllib

from flask import current_app, session, jsonify
from requests.exceptions import ConnectionError, Timeout
import slumber
from slumber.exceptions import SlumberBaseException
import json

from cla_common.constants import ELIGIBILITY_STATES
from cla_public.apps.checker.constants import CATEGORIES
from cla_public.libs.api_proxy import on_timeout
from cla_public.libs.utils import get_locale
import datetime


log = logging.getLogger(__name__)
CALLBACK_API_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


class ApiError(Exception):
    def __init__(self, *args, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
        super(ApiError, self).__init__(*args)


class AlreadySavedApiError(Exception):
    pass


def get_api_connection():
    return slumber.API(
        current_app.config["BACKEND_API"]["url"],
        timeout=current_app.config["API_CLIENT_TIMEOUT"],
        extra_headers={"Accept-Language": get_locale()},
    )


def money_interval(amount, interval="per_month"):
    return {"per_interval_value": amount, "interval_period": interval}


def initialise_eligibility_check(check):
    """Initialize the eligibility check API payload so that we will avoid
    getting 'unknown' eligibility all the time
    """

    def set_(dict_, path, value):
        key, _, rest = path.partition(".")
        if rest:
            dict_[key] = dict_.get(key, {})
            set_(dict_[key], rest, value)
        else:
            dict_[key] = dict_.get(key, value)

    set_(check, "you.income.earnings", money_interval(0))
    set_(check, "you.income.benefits", money_interval(0))
    set_(check, "you.income.tax_credits", money_interval(0))
    set_(check, "you.income.child_benefits", money_interval(0))
    set_(check, "you.income.other_income", money_interval(0))
    set_(check, "you.income.self_employment_drawings", money_interval(0))
    set_(check, "you.income.maintenance_received", money_interval(0))
    set_(check, "you.income.pension", money_interval(0))
    set_(check, "you.income.total", 0)
    set_(check, "you.income.self_employed", False)
    set_(check, "you.savings.credit_balance", 0)
    set_(check, "you.savings.investment_balance", 0)
    set_(check, "you.savings.total", 0)
    set_(check, "you.savings.asset_balance", 0)
    set_(check, "you.savings.bank_balance", 0)
    set_(check, "you.deductions.income_tax", money_interval(0))
    set_(check, "you.deductions.mortgage", money_interval(0))
    set_(check, "you.deductions.childcare", money_interval(0))
    set_(check, "you.deductions.rent", money_interval(0))
    set_(check, "you.deductions.maintenance", money_interval(0))
    set_(check, "you.deductions.national_insurance", money_interval(0))
    set_(check, "you.deductions.criminal_legalaid_contributions", 0)
    set_(check, "partner.income.earnings", money_interval(0))
    set_(check, "partner.income.benefits", money_interval(0))
    set_(check, "partner.income.tax_credits", money_interval(0))
    set_(check, "partner.income.child_benefits", money_interval(0))
    set_(check, "partner.income.other_income", money_interval(0))
    set_(check, "partner.income.self_employment_drawings", money_interval(0))
    set_(check, "partner.income.maintenance_received", money_interval(0))
    set_(check, "partner.income.pension", money_interval(0))
    set_(check, "partner.income.total", 0)
    set_(check, "partner.income.self_employed", False)
    set_(check, "partner.savings.credit_balance", 0)
    set_(check, "partner.savings.investment_balance", 0)
    set_(check, "partner.savings.total", 0)
    set_(check, "partner.savings.asset_balance", 0)
    set_(check, "partner.savings.bank_balance", 0)
    set_(check, "partner.deductions.income_tax", money_interval(0))
    set_(check, "partner.deductions.mortgage", money_interval(0))
    set_(check, "partner.deductions.childcare", money_interval(0))
    set_(check, "partner.deductions.rent", money_interval(0))
    set_(check, "partner.deductions.maintenance", money_interval(0))
    set_(check, "partner.deductions.national_insurance", money_interval(0))
    set_(check, "partner.deductions.criminal_legalaid_contributions", 0)
    set_(check, "dependants_young", 0)
    set_(check, "dependants_old", 0)
    set_(check, "on_passported_benefits", False)
    set_(check, "on_nass_benefits", False)
    set_(check, "specific_benefits", {})

    return check


API_MESSAGE_WARNINGS = ["Case with this Eligibility check already exists."]


def log_api_errors_to_sentry(fn):
    def wrapped(*args, **kwargs):
        sentry = getattr(current_app, "sentry", None)
        try:
            return fn(*args, **kwargs)
        except (ConnectionError, Timeout, SlumberBaseException) as e:
            response = getattr(e, "response", None)
            content = getattr(e, "content", "")

            try:
                errors = json.loads(content)
            except ValueError:
                errors = {}

            if errors.get("eligibility_check", None) == API_MESSAGE_WARNINGS:
                raise AlreadySavedApiError(API_MESSAGE_WARNINGS[0])

            if sentry:
                sentry.captureException(data=errors)
            else:
                log.warning("Failed posting to API: {0}, Response: {1}".format(e, content))

            raise ApiError(e, response=response, errors=errors)

    return wrapped


def ignore_api_error(fun):
    def inner(*args, **kwargs):
        try:
            return fun(*args, **kwargs)
        except ApiError:
            return None

    return inner


@log_api_errors_to_sentry
def get_case_ref_from_api(form=None, payload={}):
    backend = get_api_connection()
    reference = session.checker.get("eligibility_check")

    response = backend.eligibility_check(reference).case_ref.get()
    session.checker["case_ref"] = response["reference"]


@log_api_errors_to_sentry
def post_to_eligibility_check_api(form=None, payload={}):
    backend = get_api_connection()
    reference = session.checker.get("eligibility_check")
    payload = form.api_payload() if form else payload

    if reference is None:
        payload = initialise_eligibility_check(payload)
        response = backend.eligibility_check.post(payload)
        session.checker["eligibility_check"] = response["reference"]
    else:
        backend.eligibility_check(reference).patch(payload)


@on_timeout(response=(ELIGIBILITY_STATES.UNKNOWN, []))
def post_to_is_eligible_api():
    backend = get_api_connection()
    reference = session.checker.get("eligibility_check")

    if reference:
        response = backend.eligibility_check(reference).is_eligible().post({})
        return response.get("is_eligible"), response.get("reasons")
    return None, None


def should_attach_eligibility_check():
    return "eligibility_check" in session.checker


def attach_eligibility_check(payload):
    payload["eligibility_check"] = session.checker.get("eligibility_check")


@log_api_errors_to_sentry
def post_to_case_api(form):
    backend = get_api_connection()
    payload = form.api_payload()

    if should_attach_eligibility_check():
        attach_eligibility_check(payload)

    response = backend.case.post(payload)
    session.checker["case_ref"] = response["reference"]


@on_timeout(response="[]")
def get_organisation_list(**kwargs):
    kwargs["page_size"] = 100
    key = "organisation_list_%s" % urllib.urlencode(kwargs)
    organisation_list = current_app.cache.get(key)
    if not organisation_list:
        backend = get_api_connection()
        api_response = backend.organisation.get(**kwargs)
        organisation_list = api_response["results"]

        one_day = 24 * 60 * 60
        current_app.cache.set(key, organisation_list, timeout=one_day)

    return organisation_list


def get_ordered_organisations_by_category(**kwargs):
    organisations = get_organisation_list(**kwargs)
    categories = OrderedDict((name, []) for field, name, description in CATEGORIES)
    for organisation in organisations:
        for cat in organisation["categories"]:
            if cat["name"] in categories:
                categories[cat["name"]].append(organisation)
                break
    return categories


@on_timeout(response="[]")
@log_api_errors_to_sentry
def get_valid_callback_timeslots_on_date(date, is_third_party_callback=False):
    """Lists the times where a callback slot is available from the backend API as list of datetimes.

    Parameters:
        date: A datetime.date of the requested query date.
        is_third_party_callback: Third party callbacks are not affected by capacity

    Returns:
        List[Datetimes]: List of valid datetimes.
    """
    valid_callback_times = []
    
    backend = get_api_connection()
    slots = backend.callback_time_slots.get(third_party_callback=is_third_party_callback)["slots"]
    slots = [datetime.datetime.strptime(slot, CALLBACK_API_DATETIME_FORMAT) for slot in slots]
    
    valid_callback_times = filter(lambda slot_date: slot_date.date() == date, slots)
    return valid_callback_times
        
@on_timeout(response="[]")
@log_api_errors_to_sentry
def get_valid_callback_days(include_today=True):
    """Get the days where a callback slot is available from the backend API as list of datetimes.

    Returns:
        List[Datetimes]: List of valid datetimes.
    """
    backend = get_api_connection()
    slots = backend.callback_time_slots.get()["slots"]    
    valid_callback_days = set(datetime.datetime.strptime(slot, CALLBACK_API_DATETIME_FORMAT).date() for slot in slots)
    
    if not include_today:
        today = datetime.datetime.today().date()
        if today in valid_callback_days:
            valid_callback_days.remove(today)

    valid_callback_days = [datetime.datetime.combine(day, datetime.time(0, 0)) for day in valid_callback_days]
    return sorted(valid_callback_days)

@ignore_api_error
@log_api_errors_to_sentry
def post_reasons_for_contacting(form=None, payload={}):
    backend = get_api_connection()
    payload = form.api_payload() if form else payload
    return backend.reasons_for_contacting.post(payload)


@ignore_api_error
@log_api_errors_to_sentry
def update_reasons_for_contacting(reference, form=None, payload={}):
    backend = get_api_connection()
    payload = form.api_payload() if form else payload
    return backend.reasons_for_contacting(reference).patch(payload)
