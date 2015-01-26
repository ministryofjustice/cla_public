import datetime
from itertools import ifilter, islice, takewhile
import requests

from flask import current_app

from cla_common.call_centre_availability import *


def load_bank_holidays():
    timeout = current_app.config.get('API_CLIENT_TIMEOUT', None)
    holidays = requests.get(BANK_HOLIDAYS_URL, timeout=timeout).json()['events']
    return map(get_date, holidays)


def cache_bank_holidays(bank_holidays):
    one_year = 365 * 24 * 60 * 60
    current_app.cache.set('bank_holidays', bank_holidays, timeout=one_year)


def bank_holidays():
    bank_holidays = current_app.cache.get('bank_holidays')
    if not bank_holidays:
        bank_holidays = load_bank_holidays()
        cache_bank_holidays(bank_holidays)
    return bank_holidays


def time_choice(time):
    return (
        time.strftime('%H%M'),
        time.strftime('%I:%M %p').lstrip('0'))


def suffix(d):
    return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')


def day_choice(day):
    return (
        day.strftime('%Y%m%d'),
        '%s %s%s' % (
            day.strftime('%A'),
            day.strftime('%d').lstrip('0'),
            suffix(day.day)))
