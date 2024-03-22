from cla_public.apps.checker.api import get_api_connection, log_api_errors_to_sentry
from cla_public.libs.api_proxy import on_timeout
import datetime

CALLBACK_API_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


@on_timeout(response="[]")
@log_api_errors_to_sentry
def get_valid_callback_slots(num_days=7, is_third_party_callback=False):
    """Gets a list of slots where a callback slot is available from the backend API as list of datetimes.

    Parameters:
        num_days: The number of days worth of slots to request
        is_third_party_callback: Third party callbacks are not affected by capacity

    Returns:
        List[Datetimes]: List of valid datetimes.
    """
    backend = get_api_connection()
    slots = backend.callback_time_slots.get(num_days=num_days, third_party_callback=is_third_party_callback)["slots"]
    slots = [datetime.datetime.strptime(slot, CALLBACK_API_DATETIME_FORMAT) for slot in slots]

    return slots


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
    
    slots = get_valid_callback_slots(num_days=7, is_third_party_callback=is_third_party_callback)
    
    valid_callback_times = filter(lambda slot_date: slot_date.date() == date, slots)
    return valid_callback_times
        
@on_timeout(response="[]")
@log_api_errors_to_sentry
def get_valid_callback_days(include_today=True, is_third_party_callback=False):
    """Get the days where a callback slot is available from the backend API as list of datetimes.

    Returns:
        List[Datetimes]: List of valid datetimes.
    """
    slots = get_valid_callback_slots(num_days=7, is_third_party_callback=is_third_party_callback) 
    valid_callback_days = set(slot.date() for slot in slots)
    
    if not include_today:
        today = datetime.datetime.today().date()
        if today in valid_callback_days:
            valid_callback_days.remove(today)

    valid_callback_days = [datetime.datetime.combine(day, datetime.time(0, 0)) for day in valid_callback_days]
    return sorted(valid_callback_days)