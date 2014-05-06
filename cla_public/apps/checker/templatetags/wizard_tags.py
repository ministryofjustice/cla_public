from django import template
from django.utils.translation import ugettext_lazy as _
from django.forms.formsets import BaseFormSet

from cla_common.forms import MultipleFormsForm
from cla_common.templatetags.helpers import field_from_name

register = template.Library()


class WizardErrorsNode(template.Node):
    def __init__(self, form, var_name):
        self.form = template.Variable(form)
        self.var_name = var_name


    def get_form_error(self, form):
        if not form.errors:
            return None

        return self._get_form_error(form)

    def _get_form_error(self, form):

        if isinstance(form, MultipleFormsForm):
            return self._get_form_error(form.form_dict().values())

        _errors = []
        if isinstance(form, BaseFormSet) or isinstance(form, list):
            if hasattr(form, 'non_form_errors'):
                non_form_errors = form.non_form_errors()
                if non_form_errors:
                    field_obj = field_from_name(form[0], form[0].fields.keys()[0])
                    _errors += [(field_obj, non_form_errors)]
            for sub_form in form:
                _errors += self._get_form_error(sub_form)
        else:
            for field, errors in form.errors.items():
                field_obj = field_from_name(form, field)
                _errors.append((field_obj, errors))

        return _errors

    def render(self, context):
        form = self.form.resolve(context)

        context[self.var_name] = self.get_form_error(form)
        return ''


import re
@register.tag
def get_wizard_errors(parser, token):
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires arguments" % token.contents.split()[0])

    m = re.search(r'(.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError("%r tag had invalid arguments" % tag_name)
    form, var_name = m.groups()
    return WizardErrorsNode(form, var_name)
