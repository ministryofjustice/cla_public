# coding: utf-8
"Checker specific template filters"

from cla_public.apps.base import base


@base.app_template_filter()
def selected_option(field, selected=None):
    options_dict = dict(field.choices)
    if not selected:
        selected = field.data
    return options_dict.get(selected)
