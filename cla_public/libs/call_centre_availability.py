import datetime
from itertools import ifilter, islice, takewhile
import requests

from flask import current_app


BANK_HOLIDAYS_URL = 'https://www.gov.uk/bank-holidays/england-and-wales.json'


def current_datetime():
    # this function is to make unit testing simpler
    return datetime.datetime.now()


def in_the_past(time):
    return current_datetime() > time


def before_9am(time):
    return time.time() < datetime.time(9, 0)


def after_8pm(time):
    return time.time() >= datetime.time(20, 0)


def on_sunday(time):
    return time.weekday() == 6


def parse_date(text):
    return datetime.datetime.strptime(text, '%Y-%m-%d')


def get_date(bank_holiday):
    return parse_date(bank_holiday['date'])


def load_bank_holidays():
    if current_app.config.get('TESTING', False):
        return [
            datetime.datetime(2014, 12, 25),
            datetime.datetime(2014, 12, 26),
            datetime.datetime(2015, 1, 1)]
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


def on_bank_holiday(time):
    day = datetime.datetime.combine(time.date(), datetime.time())
    return day in bank_holidays()


def on_saturday(time):
    return time.weekday() == 5


def on_weekday(time):
    return time.weekday() < 5


def after_1230(time):
    return time.time() >= datetime.time(12, 30)


def is_today(time):
    return time.date() == current_datetime().date()


def too_late(time):
    one_hour = datetime.timedelta(minutes=60)
    now = current_datetime()
    return time.time() <= (now + one_hour).time()


def available(dt, ignore_time=False):
    if not (in_the_past(dt) or on_sunday(dt) or on_bank_holiday(dt)):
        return ignore_time or not (
            (before_9am(dt) or after_8pm(dt)) or
            (on_saturday(dt) and after_1230(dt)) or
            (is_today(dt) and too_late(dt)))
    return False


def every_interval(time, days=0, hours=0, minutes=0):
    interval = datetime.timedelta(days=days, hours=hours, minutes=minutes)
    while True:
        yield time
        time += interval


def available_days(num):
    days = every_interval(current_datetime(), days=1)
    available_day = lambda day: available(day, ignore_time=True)
    return list(islice(ifilter(available_day, days), num))


def time_slots(day=None):
    if not day:
        day = datetime.date(9999, 1, 1)  # a weekday in the future
    start = datetime.datetime.combine(day, datetime.time(9))
    same_day = lambda x: x.date() == day
    every_15m = takewhile(same_day, every_interval(start, minutes=15))
    return list(ifilter(available, every_15m))


def today_slots(*args):
    return time_slots(current_datetime().date())


def tomorrow_slots(*args):
    tomorrow = current_datetime() + datetime.timedelta(days=1)
    return time_slots(tomorrow.date())


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

