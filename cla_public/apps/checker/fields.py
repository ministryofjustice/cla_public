# -*- coding: utf-8 -*-
"Custom form fields"

import re

from flask import session
from wtforms import Form as NoCsrfForm
from wtforms import FormField, BooleanField, IntegerField, Label, RadioField, \
    SelectField, SelectMultipleField, widgets, FieldList
from wtforms.validators import ValidationError, StopValidation, Optional
from wtforms.compat import text_type

from cla_common.constants import CONTACT_SAFETY, ADAPTATION_LANGUAGES
from cla_public.apps.checker.constants import MONEY_INTERVALS, NO, YES

partner_regex = re.compile(r'(and/or|and|or) your partner')

LANG_CHOICES = filter(
    lambda x: x[0] not in ('ENGLISH', 'WELSH'),
    [('', '-- Choose a language --')] + ADAPTATION_LANGUAGES)


class ZeroOrNoneValidator(object):
    """Form Validator that checks if the minimum is min_val (or greater)
    or None."""

    def __init__(self, min_val=0, max_val=None, message=None):
        self.min_val = min_val
        self.max_val = max_val
        self.message = message

    def __call__(self, form, field):
        # This code is copied from NumberRange. It is identical except
        # it will short-circuit if data is None and not raise a
        # ValidationError exception.
        data = field.data
        if (self.min_val is not None and data < self.min_val) or \
                (self.max_val is not None and data > self.max_val):
            if data is None:
                # We *also* need this as we need to clear out any
                # field errors generated from IntegerField saying
                # "None" is not a valid integer.
                field.errors[:] = []
                raise StopValidation()
            message = self.message
            if message is None:
                # we use %(min_val)s interpolation to support floats, None, and
                # Decimals without throwing a formatting exception.
                if self.max_val is None:
                    message = field.gettext('Number must be at least %(min_val)s.')
                elif self.min_val is None:
                    message = field.gettext('Number must be at most %(max_val)s.')
                else:
                    message = field.gettext('Number must be between %(min_val)s and %(max_val)s.')

            raise ValidationError(message % dict(min_val=self.min_val, max_val=self.max_val))


class DynamicPartnerLabel(Label):

    def __call__(self, text=None, **kwargs):
        if not text:
            text = self.text
        if not session.has_partner and 'partner' in text:
            text = re.sub(partner_regex, '', text)
        return super(DynamicPartnerLabel, self).__call__(text, **kwargs)


class PartnerMixin(object):

    @property
    def label(self):
        if not hasattr(self, '_label'):
            return None
        return self._label

    @label.setter
    def label(self, value):
        self._label = DynamicPartnerLabel(self.id, value.text)

    @property
    def description(self):
        if not hasattr(self, '_description'):
            return None
        desc = self._description
        if not session.has_partner and 'partner' in self._description:
            desc = re.sub(partner_regex, '', desc)
        return desc

    @description.setter
    def description(self, value):
        self._description = value


class DescriptionRadioField(RadioField):
    """RadioField with a description for each radio button, not just for the
    group.

    The choices kwargs field takes a list of triples.

    Format:

    choices=[(name, label, description), ...]
    """

    def __init__(self, *args, **kwargs):
        self.field_names = []
        self.more_infos = []
        self.descriptions = []
        choices = []
        for name, label, description in kwargs.get('choices', []):
            self.field_names.append(name)
            self.descriptions.append(description)
            choices.append((name, label))
        if choices:
            kwargs['choices'] = choices
        super(DescriptionRadioField, self).__init__(*args, **kwargs)

    def __iter__(self):
        options = super(DescriptionRadioField, self).__iter__()
        for index, option in enumerate(options):
            option.description = self.descriptions[index]
            option.field_name = self.field_names[index]
            try:
                option.more_info = self.more_infos[index]
            except IndexError:
                option.more_info = None
            yield option

    def add_more_infos(self, more_infos):
        self.more_infos = more_infos


class YesNoField(RadioField):
    """Yes/No radio button field"""

    def __init__(self, label=None, validators=None, **kwargs):
        choices = [(YES, 'Yes'), (NO, 'No')]
        super(YesNoField, self).__init__(
            label=label, validators=validators, coerce=text_type,
            choices=choices, **kwargs)


class MoneyField(IntegerField):

    def __init__(self, label=None, validators=None, min_val=0, max_val=None,
                 **kwargs):
        super(MoneyField, self).__init__(label, validators, **kwargs)
        self.min_val = min_val
        self.max_val = max_val

    def process_formdata(self, valuelist):
        if valuelist:
            pounds, _, pence = valuelist[0].partition('.')
            pounds = re.sub(r'[\s,]+', '', pounds)

            if pence and len(pence) != 2:
                self.data = None
                raise ValueError(self.gettext(u'Not a valid amount'))

            try:
                self.data = int(pounds) * 100
                if pence:
                    self.data += int(pence)
            except ValueError:
                self.data = None
                raise ValueError(self.gettext(u'Not a valid amount'))

            if self.min_val is not None and self.data < self.min_val:
                self.data = None
                raise ValueError(self.gettext(
                    u'Amount must be greater than £{:.2f}'.format(
                        self.min_val / 100.0)))

            if self.max_val is not None and self.data > self.max_val:
                self.data = None
                raise ValueError(self.gettext(
                    u'Amount must be less than £{:.2f}'.format(
                        self.max_val / 100.0)))


class MoneyIntervalForm(NoCsrfForm):
    """Money amount and interval subform"""
    amount = MoneyField(validators=[Optional()])
    interval = SelectField('', choices=MONEY_INTERVALS)

    def validate(self, *args, **kwargs):
        valid_amount = self.amount.validate(self)
        amount_not_set = self.amount.data is None
        nonzero_amount = self.amount.data > 0
        interval_selected = self.interval.data != ''

        if not valid_amount:
            # default field validation should set error message
            return False

        if interval_selected and amount_not_set:
            self.interval.errors = (u'Not a valid amount',)
            return False

        if not interval_selected and nonzero_amount:
            self.interval.errors = (u'Please select an interval')
            return False

        return True


class MoneyIntervalField(FormField):
    """Convenience class for FormField(MoneyIntervalForm)"""

    widget = widgets.ListWidget()

    def __init__(self, *args, **kwargs):
        super(MoneyIntervalField, self).__init__(
            MoneyIntervalForm, *args, **kwargs)


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class PropertyList(FieldList):
    def remove(self, index):
        del self.entries[index]
        self.last_index -= 1


class PartnerMoneyIntervalField(MoneyIntervalField, PartnerMixin):
    pass


class PartnerIntegerField(IntegerField, PartnerMixin):
    pass


class PartnerYesNoField(YesNoField, PartnerMixin):
    pass


class PartnerMultiCheckboxField(MultiCheckboxField, PartnerMixin):
    pass


class AdaptationsForm(NoCsrfForm):
    bsl_webcam = BooleanField(u'BSL - Webcam')
    minicom = BooleanField(u'Minicom')
    text_relay = BooleanField(u'Text Relay')
    welsh = BooleanField(u'Welsh')
    is_other_language = BooleanField(u'Other language')
    other_language = SelectField(
        u'Language required:',
        choices=(LANG_CHOICES))


class PartnerMoneyField(MoneyField, PartnerMixin):
    pass
