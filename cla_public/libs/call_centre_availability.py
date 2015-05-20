from copy import copy
import datetime
import requests

from flask import current_app

from cla_common import call_centre_availability
from cla_common.call_centre_availability import BankHolidays, available, \
    available_days, time_slots, today_slots, on_bank_holiday, Hours


class FlaskCacheBankHolidays(BankHolidays):

    def init_cache(self):
        self._cache = current_app.cache

    def _load_dates(self):
        timeout = current_app.config.get('API_CLIENT_TIMEOUT', None)
        return requests.get(self.url, timeout=timeout).json()['events']


# monkey patch cla_common to avoid invoking django code
call_centre_availability.bank_holidays = lambda: FlaskCacheBankHolidays()


def time_choice(time):
    return (
        time.strftime('%H%M'),
        time.strftime('%I:%M %p').lstrip('0'))


def suffix(d):
    if 11 <= d <= 13:
        return 'th'
    return {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')


def day_choice(day):
    return (
        day.strftime('%Y%m%d'),
        '%s %s%s' % (
            day.strftime('%A'),
            day.strftime('%d').lstrip('0'),
            suffix(day.day)))


def monday_after_11_hours():
    return Hours(datetime.time(11, 0), datetime.time(20, 0))


def monday_before_11am_between_eod_friday_and_monday(dt):
    now = call_centre_availability.current_datetime()
    after_hours_friday = now.weekday() == 4 and now.hour > 19
    weekend = now.weekday() in (5, 6)
    first_work_day = 0
    while on_bank_holiday(dt - datetime.timedelta(days=first_work_day+1)):
        first_work_day += 1
    monday_before_11am = dt.weekday() == first_work_day and dt.hour < 11
    return (after_hours_friday or weekend) and monday_before_11am
