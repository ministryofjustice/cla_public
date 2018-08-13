# -*- coding: utf-8 -*-
"Jinja custom filters"

import re
from urlparse import urlparse, parse_qs
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


@base.app_template_filter()
def url_to_human(value):
    return re.sub(r'(^https?://)|(/$)', '', value)


@base.app_template_filter()
def human_to_url(value):
    return re.sub(r'^((?!https?://).*)', r'http://\1', value)


@base.app_template_filter()
def query_to_dict(value, prop=None):
    result = parse_qs(urlparse(value).query)
    if not prop:
        return result

    return result.get(prop, [])
