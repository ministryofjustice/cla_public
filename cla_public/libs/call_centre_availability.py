import requests

from flask import current_app

from cla_common import call_centre_availability
from cla_common.call_centre_availability import BankHolidays, available, \
    available_days, current_datetime, time_slots, today_slots


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
