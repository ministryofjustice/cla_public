# -*- coding: utf-8 -*-
"Datetime formatting jinja filter"

from cla_public.apps.base import base
from babel.dates import format_datetime


@base.app_template_filter()
def datetime(dt, format='medium', locale='en_GB'):
    if format == 'full':
        format = "EEEE, d MMMM y 'at' HH:mm"
    elif format == 'medium':
        format = "EE, dd/MM/y 'at' h:mma"
    elif format == 'short':
        format = "dd/MM/y, h:mma"
    return format_datetime(dt, format, locale=locale)
