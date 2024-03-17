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
    "cy": ["Ion", "Chwe", "Maw", "Ebr", "Mai", "Meh", "Gor", "Awst", "Med", "Hyd", "Tach", "Rhag"]
}

SHORT_DAYS = {
    "en": ["Mon", "Tues", "Weds", "Thurs", "Fri", "Sat", "Sun"],
    "cy": ["Llun", "Maw", "Mer", "Iau", "Gwe", "Sad", "Sul"]
}

def format_time_welsh_suffix(time):
    if time >= EVENING_NIGHT:
        return "yh"
    elif time >= AFTERNOON:
        return "yp"
    else:
        return "yb"


def format_time(dt):
    if isinstance(dt, datetime.datetime):
        time = dt.time()
    else:
        time = dt
    display_format = "%I:%M"
    if time.minute == 0:
        display_format = "%I"
    display_string = time.strftime(display_format).lstrip("0")

    time_suffix = time.strftime("%p").lower()

    return "%s%s" % (display_string, time_suffix)


def time_choice(time):
    end = time + datetime.timedelta(minutes=30)
    display_string = format_time(time) + " to " + format_time(end)
    if get_locale().startswith("cy"):
        display_string = format_time(time) + " i " + format_time(end)
    return time.strftime("%H%M"), display_string


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
    local = "cy" if get_locale().startswith("cy") else "en"
    return SHORT_MONTHS[local][day.month - 1]

def get_short_day_str(day):
    local = "cy" if get_locale().startswith("cy") else "en"
    return SHORT_DAYS[local][day.weekday()]

def day_choice(day):
    return day.strftime("%Y%m%d"), "%s %s %s" % (get_short_day_str(day), day.strftime("%d").lstrip("0"), get_short_month_str(day))
