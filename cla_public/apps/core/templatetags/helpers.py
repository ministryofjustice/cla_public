from django import template
from django.template.defaultfilters import stringfilter
from numbers import Number
from collections import Iterable

register = template.Library()

@stringfilter
def unslug(name):
    return name.replace('_', ' ').capitalize()

register.filter('unslug', unslug)


@register.filter(is_safe=True)
def in_pounds(value):
    if isinstance(value, Number):
        value = value / 100.0
        return u'{val:.2f}'.format(val=value)
    return value


@register.filter()
def field_from_name(form, name):
    return form[name]


@register.filter()
def any_true(l):
    if isinstance(l, Iterable):
        return any(l)
    else: 
        return bool(l)