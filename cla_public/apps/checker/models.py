# form error message override
from django.forms import Field
from django.utils.translation import ugettext_lazy
Field.default_error_messages = {
    'required': ugettext_lazy("cannot be blank"),
    }