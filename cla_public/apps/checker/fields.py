from decimal import Decimal, InvalidOperation
from django import forms
from django.core import validators
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _

from cla_common.helpers import MoneyInterval

BOOL_CHOICES = ((1, _('Yes')), (0, _('No')))

TWO_DP = Decimal('.01')
ZERO_DP = Decimal('1')

class RadioBooleanField(forms.TypedChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['coerce'] = kwargs.pop('coerce', int)
        kwargs['widget'] = forms.RadioSelect
        kwargs['choices'] = kwargs.pop('choices', BOOL_CHOICES)

        super(RadioBooleanField, self).__init__(*args, **kwargs)


class MoneyIntervalWidget(widgets.MultiWidget):

    def __init__(self, attrs=None):

        intervals = MoneyInterval.get_intervals_for_widget()

        _widgets = (
            widgets.NumberInput(attrs=attrs),
            widgets.Select(attrs=attrs, choices=intervals)
        )
        super(MoneyIntervalWidget, self).__init__(_widgets, attrs)

    def decompress(self, value):
        if value and isinstance(value, dict):
            return [value['earnings_per_interval_value'], value['earnings_interval_period']]
        return [None, None]

    def format_output(self, rendered_widgets):

        # there should be a number input and a dropdown
        if len(rendered_widgets) == 2:
            # the string added here separates the two inputs and is
            # HTML so OK add tags etc.
            rendered_widgets.insert(1, " per ")
        return u''.join(rendered_widgets)


class MoneyIntervalField(forms.MultiValueField):
    widget = MoneyIntervalWidget

    def __init__(self, max_value=2500000, min_value=0, step=None, *args, **kwargs):
        self.max_value, self.min_value, self.step = max_value, min_value, step or '0.01'

        fields = [
            forms.DecimalField(max_value=max_value, min_value=min_value, decimal_places=2),
            forms.CharField(),
        ]

        super(MoneyIntervalField, self).__init__(fields, *args, **kwargs)

#         if max_value is not None:
#             self.validators.append(validators.MaxValueValidator(max_value))
#         if min_value is not None:
#             self.validators.append(validators.MinValueValidator(min_value))

    def compress(self, data_vals):
        if len(data_vals) == 2:
            #value = int(Decimal(data_vals[0]).quantize(ZERO_DP))*100
            #compressed = "%s-%s" % (value, data_vals[1])
            #return compressed
            mi = MoneyInterval(interval_period=data_vals[1])
            mi.set_as_pounds(per_interval_value=data_vals[0])
            # a serialiser has been deemed too much
            return { 'earnings_interval_period' : mi.interval_period,
                     'earnings_per_interval_value' : mi.per_interval_value,
                     'per_month' :  mi.as_monthly()
                   }
        return None

    def widget_attrs(self, widget):
        attrs = super(MoneyIntervalField, self).widget_attrs(widget)

        if isinstance(widget, forms.NumberInput):
            if self.min_value is not None:
                attrs['min'] = self.min_value
            if self.max_value is not None:
                attrs['max'] = self.max_value
            if self.step is not None:
                attrs['step'] = self.step

        return attrs


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
