import datetime
from cla_public.libs.utils import get_locale
from flask.ext.babel import lazy_gettext as _


AFTERNOON = datetime.time(hour=12, minute=0)
EVENING_NIGHT = datetime.time(hour=18, minute=0)
WELSH_ORDINALS = {
    "1": "af",
    "2": "il",
    "3": "ydd",
    "4": "ydd",
    "5": "ed",
    "6": "ed",
    "7": "fed",
    "8": "fed",
    "9": "fed",
    "10": "fed",
    "11": "eg",
    "12": "fed",
    "13": "eg",
    "14": "eg",
    "15": "fed",
    "16": "eg",
    "17": "eg",
    "18": "fed",
    "19": "eg",
    "20": "fed",
}
WELSH_DEFAULT_ORDINAL = "ain"

SHORT_MONTHS = {
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "cy": ["Ion", "Chwe", "Maw", "Ebr", "Mai", "Meh", "Gor", "Awst", "Med", "Hyd", "Tach", "Rhag"],
}

SHORT_DAYS = {
    "en": ["Mon", "Tues", "Weds", "Thurs", "Fri", "Sat", "Sun"],
    "cy": ["Llun", "Maw", "Mer", "Iau", "Gwe", "Sad", "Sul"],
}


def format_time_welsh_suffix(time):
    if time >= EVENING_NIGHT:
        return "yh"
    elif time >= AFTERNOON:
        return "yp"
    else:
        return "yb"


def format_time(dt):
    time = dt.time() if isinstance(dt, datetime.datetime) else dt
    time_format = "%-I.%M" if time.minute != 0 else "%-I"
    formatted_time = time.strftime(time_format)

    time_suffix = time.strftime("%p").lower()

    return "%s%s" % (formatted_time, time_suffix)


def format_time_option(start_time):
    end_time = start_time + datetime.timedelta(minutes=30)
    preposition = "to" if get_locale().startswith("en") else "i"

    # Example time format: 9am to 9.30am
    formatted_time = "{start_time} {preposition} {end_time}".format(
        start_time=format_time(start_time), preposition=preposition, end_time=format_time(end_time)
    )
    return start_time.strftime("%H%M"), formatted_time


def suffix_day_welsh(day):
    return WELSH_ORDINALS.get(str(day), WELSH_DEFAULT_ORDINAL)


def suffix_day_english(day):
    if 11 <= day <= 13:
        return _("th")
    return {1: _("st"), 2: _("nd"), 3: _("rd")}.get(day % 10, _("th"))


def suffix(day):
    if get_locale()[:2] == "cy":
        return suffix_day_welsh(day)

    return suffix_day_english(day)


def get_short_month_str(day):
    return SHORT_MONTHS[get_locale()][day.month - 1]


def get_short_day_str(day):
    return SHORT_DAYS[get_locale()][day.weekday()]


def format_date_option(day):
    # Example date format: Mon 1 Jan
    formatted_date = "{short_day_name} {day_in_month} {short_month_name}".format(
        short_day_name=get_short_day_str(day),
        day_in_month=day.strftime("%-d"),
        short_month_name=get_short_month_str(day),
    )
    return day.strftime("%Y%m%d"), formatted_date
