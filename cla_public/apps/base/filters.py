from cla_public.apps.base import base
from babel.dates import format_datetime
from dateutil import parser
import re

@base.app_template_filter()
def datetime(dt, format='medium', locale='en_GB'):
    if format == 'full':
        format="EEEE, d MMMM y 'at' HH:mm"
    elif format == 'medium':
        format="EE, dd/MM/y 'at' h:mma"
    elif format == 'short':
        format="dd/MM/y, h:mma"
    return format_datetime(dt, format, locale=locale)

@base.app_template_filter('quoted')
def quoted(s):
    l = re.findall('\'([^\']*)\.', str(s))
    if l:
        return l[0]
    return None
