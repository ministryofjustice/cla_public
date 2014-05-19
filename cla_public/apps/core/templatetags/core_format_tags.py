from django import template
from django.contrib.humanize.templatetags.humanize import ordinal

register = template.Library()

@register.filter()
def ordinal_from_count(count, total):
    if total == 1:
        return ""
    return ordinal(count)