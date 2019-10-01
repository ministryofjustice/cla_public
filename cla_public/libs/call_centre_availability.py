import datetime

import requests
from flask import current_app
from cla_common import call_centre_availability
from cla_common.call_centre_availability import BankHolidays
from cla_common.constants import CALLBACK_WINDOW_TYPES


class FlaskCacheBankHolidays(BankHolidays):
    def init_cache(self):
        self._cache = current_app.cache

    def _load_dates(self):
        timeout = current_app.config.get("API_CLIENT_TIMEOUT", None)
        return requests.get(self.url, timeout=timeout).json()["events"]


# monkey patch cla_common to avoid invoking django code
call_centre_availability.bank_holidays = lambda: FlaskCacheBankHolidays()


def time_choice(time):
    display_format = "%I:%M %p"
    display_string = time.strftime(display_format)
    if current_app.config["CALLBACK_WINDOW_TYPE"] == CALLBACK_WINDOW_TYPES.HALF_HOUR_WINDOW:
        end = time + datetime.timedelta(minutes=30)
        display_string = display_string + " - " + end.strftime(display_format)
    return time.strftime("%H%M"), display_string.lstrip("0")


def suffix(d):
    if 11 <= d <= 13:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")


def day_choice(day):
    return day.strftime("%Y%m%d"), "%s %s%s" % (day.strftime("%A"), day.strftime("%d").lstrip("0"), suffix(day.day))
