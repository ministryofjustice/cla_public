import datetime
from flask.ext.babel import lazy_gettext as _


def time_choice(time):
    display_format = "%I:%M %p"
    end = time + datetime.timedelta(minutes=30)
    display_string = time.strftime(display_format).lstrip("0") + " - " + end.strftime(display_format).lstrip("0")
    return time.strftime("%H%M"), display_string


def suffix(d):
    if 11 <= d <= 13:
        return _("th")
    return {1: _("st"), 2: _("nd"), 3: _("rd")}.get(d % 10, _("th"))


def day_choice(day):
    return day.strftime("%Y%m%d"), "%s %s%s" % (_(day.strftime("%A")), day.strftime("%d").lstrip("0"), suffix(day.day))
