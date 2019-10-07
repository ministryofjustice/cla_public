import datetime

import requests
from flask import current_app
from cla_common import call_centre_availability
from cla_common.call_centre_availability import BankHolidays


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
    end = time + datetime.timedelta(minutes=30)
    display_string = time.strftime(display_format) + " - " + end.strftime(display_format)
    return time.strftime("%H%M"), display_string.lstrip("0")


def suffix(d):
    if 11 <= d <= 13:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")


def day_choice(day):
    return day.strftime("%Y%m%d"), "%s %s%s" % (day.strftime("%A"), day.strftime("%d").lstrip("0"), suffix(day.day))
