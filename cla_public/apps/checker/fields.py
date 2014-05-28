from decimal import Decimal, InvalidOperation
from django import forms
from django.core import validators
from django.utils.translation import ugettext_lazy as _

BOOL_CHOICES = ((1, _('Yes')), (0, _('No')))

TWO_DP = Decimal('.01')
ZERO_DP = Decimal('1')


class RadioBooleanField(forms.TypedChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['coerce'] = kwargs.pop('coerce', int)
        kwargs['widget'] = forms.RadioSelect
        kwargs['choices'] = kwargs.pop('choices', BOOL_CHOICES)

        super(RadioBooleanField, self).__init__(*args, **kwargs)


class MoneyField(forms.Field):
    default_error_messages = {
        'invalid': _('Enter a number with up to two decimal places.'),
    }

    def __init__(self, max_value=9999999999, min_value=0, step=None, *args, **kwargs):
        self.max_value, self.min_value, self.step = max_value, min_value, step or '0.01'
        kwargs.setdefault('widget', forms.NumberInput if not kwargs.get('localize') else self.widget)
        super(MoneyField, self).__init__(*args, **kwargs)

        if max_value is not None:
            self.validators.append(validators.MaxValueValidator(max_value))
        if min_value is not None:
            self.validators.append(validators.MinValueValidator(min_value))

    def to_python(self, value):
        """
        Validates that int() can be called on the input. Returns the result
        of int(). Returns None for empty values.
        """
        value = super(MoneyField, self).to_python(value)
        if value in self.empty_values:
            return None

        if isinstance(value, bool):
            return None

        if self.localize:
            value = forms.formats.sanitize_separators(value)
        try:
            value = int(Decimal(value).quantize(TWO_DP) * 100)
        except (ValueError, TypeError, InvalidOperation):
            raise forms.ValidationError(self.error_messages['invalid'], code='invalid')
        return value

    def clean(self, value):
        value = super(MoneyField, self).clean(value)
        if value:
            value = int(Decimal(value).quantize(ZERO_DP))

        return value

    def widget_attrs(self, widget):
        attrs = super(MoneyField, self).widget_attrs(widget)

        if isinstance(widget, forms.NumberInput):
            if self.min_value is not None:
                attrs['min'] = self.min_value
            if self.max_value is not None:
                attrs['max'] = self.max_value
            if self.step is not None:
                attrs['step'] = self.step

        return attrs
