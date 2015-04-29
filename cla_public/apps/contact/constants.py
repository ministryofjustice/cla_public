# -*- coding: utf-8 -*-
"Contact constants"

from flask.ext.babel import lazy_gettext as _


DAY_TODAY = 'today'
DAY_SPECIFIC = 'specific_day'
DAY_CHOICES = (
    (DAY_TODAY, _('Call me today at')),
    (DAY_SPECIFIC, _('Call me on'))
)
