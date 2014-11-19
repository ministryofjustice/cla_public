from cla_public.apps.base import base

@base.app_template_filter()
def test(value):
    return value
