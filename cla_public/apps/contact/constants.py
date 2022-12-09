# coding: utf-8
"Contact constants"

from flask.ext.babel import lazy_gettext as _


DAY_TODAY = "today"
DAY_SPECIFIC = "specific_day"
DAY_CHOICES = ((DAY_TODAY, _("Call today")), (DAY_SPECIFIC, _("Call on another day")))
SELECT_OPTION_DEFAULT = [("", "-- Please select --")]
TIME_TODAY_VALIDATION_ERROR = u"Select what time you want to be called today"
DAY_SPECIFIC_VALIDATION_ERROR = u"Select which day you want to be called"
TIME_SPECIFIC_VALIDATION_ERROR = u"Select what time you want to be called"
