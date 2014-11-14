import re
from cla_public.apps.base import base

@base.app_template_filter()
def test(value):
    return value

@base.app_template_filter()
def split(value, pattern):
    return re.split(pattern, value)
