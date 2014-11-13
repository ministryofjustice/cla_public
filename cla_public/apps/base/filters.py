import re
from cla_public.apps.base import base

@base.app_template_filter()
def matches(value, pattern):
    return bool(re.search(pattern, value))
