# -*- coding: utf-8 -*-
"Checker forms"

import logging

from functools import partial
from flask import session
from flask_wtf import Form
from wtforms import IntegerField, StringField, TextAreaField, FieldList, FormField
from wtforms.compat import iteritems
from wtforms.validators import InputRequired, ValidationError, NumberRange

from cla_public.apps.checker.constants import CATEGORIES, BENEFITS_CHOICES, \
    NON_INCOME_BENEFITS
from cla_public.apps.checker.fields import (
    DescriptionRadioField, MoneyIntervalField, MultiCheckboxField,
    YesNoField, PartnerIntegerField, PartnerYesNoField,
    PartnerMoneyIntervalField, PartnerMultiCheckboxField,
    ZeroOrNoneValidator, AdditionalPropertyForm,
    )
from cla_public.apps.checker.form_config_parser import FormConfigParser


log = logging.getLogger(__name__)


class Struct(object):

    def __init__(self, **entries):
        self.__dict__.update(entries)


class ConfigFormMixin(object):
    def __init__(self, *args, **kwargs):
        config_path = kwargs.pop('config_path', None)

        super(ConfigFormMixin, self).__init__(*args, **kwargs)

        self.config_data = FormConfigParser(self.__class__.__name__,
                                            config_path=config_path)

        # set config attributes on the field
        for field_name, field in iteritems(self._fields):
            field_config = self.config_data.get_field_config(field_name, field)
            for attribute, value in field_config.iteritems():
                setattr(field, attribute, value)


class MultiPageForm(ConfigFormMixin, Form):
    """Stores validated form data in the session"""

    def __init__(self, formdata=None, obj=None, prefix='',
                 csrf_context=None, secret_key=None, csrf_enabled=None, *args,
                 **kwargs):
        namespace = '{0}_'.format(self.__class__.__name__)

        self_fields = lambda (key, val): \
            key.startswith(namespace)

        strip_namespace = lambda (key, val): \
            (key.replace(namespace, ''), val)

        if obj:
            obj = Struct(**dict(map(
                strip_namespace,
                filter(self_fields, obj.items()))))

        super(MultiPageForm, self).__init__(
            formdata=formdata, obj=obj, prefix=prefix,
            csrf_context=csrf_context, secret_key=secret_key,
            csrf_enabled=csrf_enabled, *args, **kwargs)


    def validate(self):
        """Store the validated field data in the session.
        If the validation failed, remove this form's field data.
        """
        success = super(MultiPageForm, self).validate()

        namespace = lambda field: '{form}_{field}'.format(
            form=self.__class__.__name__,
            field=field)

        for field_name, data in self.data.iteritems():
            key = namespace(field_name)
            if success:
                session[key] = data
            elif key in session:
                del session[key]

        return success


class ProblemForm(MultiPageForm):
    """Area of law choice"""

    categories = DescriptionRadioField(
        u'What do you need help with?',
        choices=CATEGORIES,
        coerce=unicode,
        validators=[InputRequired()])


class AboutYouForm(MultiPageForm):
    have_partner = YesNoField(
        u'Do you have a partner?',
        description=(
            u"Your partner is your husband, wife, civil partner or someone "
            u"you live with as if you’re married"))
    in_dispute = YesNoField(
        u'Are you in a dispute with your partner?',
        description=(
            u"This means a dispute over money or property following a "
            u"separation"))
    on_benefits = YesNoField(
        u'Are you on any benefits?',
        description=(
            u"Being on some benefits can help you qualify for legal aid"))
    have_children = YesNoField(
        u'Do you have any children aged 15 or under?',
        description=u"Don’t include any children who don’t live with you")
    num_children = IntegerField(u'How many?',
                                validators=[ZeroOrNoneValidator()])
    have_dependants = YesNoField(
        u'Do you have any dependants aged 16 or over?',
        description=u"People who you live with and support financially")
    num_dependants = IntegerField(u'How many?',
                                  validators=[ZeroOrNoneValidator()])
    have_savings = YesNoField(
        u'Do you have any savings, investments or any valuable items?',
        description=(
            u"Valuable items are worth over £500 each with some exceptions"))
    own_property = YesNoField(
        u'Do you own any property?',
        description=u"For example, a house, flat or static caravan")
    is_employed = YesNoField(
        u'Are you employed?',
        description=(
            u"This means working as an employee - you may be both employed "
            u"and self-employed"))
    is_self_employed = YesNoField(
        u'Are you self-employed?',
        description=(
            u"This means working for yourself - you may be both employed "
            u"and self-employed"))
    aged_60_or_over = YesNoField(u'Are you aged 60 or over?')


class AtLeastOne(object):
    """
    Valid if at least one option is checked.

    :param message:
        Error message to raise in case of a validation error.
    """

    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        if len(field.data) < 1:
            message = self.message
            if message is None:
                message = field.gettext('Must select at least one option.')
            raise ValidationError(message)


class YourBenefitsForm(MultiPageForm):
    benefits = MultiCheckboxField(
        choices=BENEFITS_CHOICES,
        validators=[AtLeastOne()])


class PropertyForm(MultiPageForm):
    is_main_home = YesNoField(
        u'Is this property your main home?',
        description=(
            u"If you are separated and no longer live in the property you "
            u"own, please answer ‘no’"))
    other_shareholders = PartnerYesNoField(
        u'Does anyone else own a share of the property?',
        description=u"Other than you and your partner")
    property_value = IntegerField(
        u'How much is the property worth?',
        description=u"Use your own estimate",
        validators=[ZeroOrNoneValidator()])
    mortgage_remaining = IntegerField(
        u'How much is left to pay on the mortgage?',
        description=(
            u"Include the full amount you owe, even if the property has "
            u"shared ownership"),
        validators=[ZeroOrNoneValidator()])
    mortgage_payments = IntegerField(
        u'How much are your monthly mortgage repayments?',
        validators=[ZeroOrNoneValidator()])
    is_rented = YesNoField(u'Does anyone pay you rent for this property?')
    rent_amount = IntegerField(u'How much rent do they pay you?',
                               validators=[ZeroOrNoneValidator()])
    in_dispute = YesNoField(
        u'Is your share of the property in dispute?',
        description=(
            u"For example, as part of the financial settlement of a divorce"))

    additional_properties = FieldList(FormField(AdditionalPropertyForm),
                                      max_entries=3)

class SavingsForm(MultiPageForm):
    savings = IntegerField(
        description=(
            u"The total amount of savings in cash, bank or building society"),
        validators=[ZeroOrNoneValidator()]
        )
    investments = IntegerField(
        description=u"This includes stocks, shares, bonds (but not property)",
        validators=[ZeroOrNoneValidator()])
    valuables = PartnerIntegerField(
        u'Valuable items you and your partner own worth over £500 each',
        description=u"Total value of any items you own with some exceptions",
        validators=[ZeroOrNoneValidator(min_val=500)])


class TaxCreditsForm(MultiPageForm):
    child_benefit = MoneyIntervalField(
        u'Child Benefit',
        description=u"The total amount you get for all your children",
        validators=[ZeroOrNoneValidator()])
    child_tax_credit = MoneyIntervalField(
        u'Child Tax Credit',
        description=u"The total amount you get for all your children",
        validators=[ZeroOrNoneValidator()])
    benefits = PartnerMultiCheckboxField(
        u'Do you or your partner get any of these benefits?',
        description=(
            u"These benefits don’t count as income. Please tick the ones you "
            u"receive."),
        choices=NON_INCOME_BENEFITS)
    other_benefits = PartnerYesNoField(
        u'Do you or your partner receive any other benefits not listed above?')
    total_other_benefit = MoneyIntervalField(
        u'Total amount of benefits not listed above',
        validators=[ZeroOrNoneValidator()])


class IncomeAndTaxForm(MultiPageForm):
    earnings = MoneyIntervalField(
        u'Wages before tax',
        description=(
            u"This includes all your wages and any earnings from "
            u"self-employment"),
        validators=[ZeroOrNoneValidator()])
    income_tax = MoneyIntervalField(
        u'Income tax',
        description=(
            u"Tax paid directly out of your wages and any tax you pay on "
            u"self-employed earnings"),
        validators=[ZeroOrNoneValidator()])
    national_insurance = MoneyIntervalField(
        u'National Insurance contributions',
        description=(
            u"Check your payslip or your National Insurance statement if "
            u"you’re self-employed"),
        validators=[ZeroOrNoneValidator()])
    working_tax_credit = MoneyIntervalField(u'Working Tax Credit',
                                            validators=[ZeroOrNoneValidator()])
    maintenance = MoneyIntervalField(
        u'Maintenance received',
        description=u"Payments you get from an ex-partner",
        validators=[ZeroOrNoneValidator()])
    pension = MoneyIntervalField(
        u'Pension received',
        description=u"Payments you receive if you’re retired",
        validators=[ZeroOrNoneValidator()])
    other_income = MoneyIntervalField(
        u'Any other income',
        description=(
            u"For example, student grants, income from trust funds, "
            u"dividends"),
        validators=[ZeroOrNoneValidator()])


class OutgoingsForm(MultiPageForm):
    rent = PartnerMoneyIntervalField(
        u'Rent',
        description=u"Money you and your partner pay your landlord")
    maintenance = PartnerMoneyIntervalField(
        u'Maintenance',
        description=(
            u"Money you and/or your partner pay to an ex-partner for their "
            u"living costs"))
    income_contribution = PartnerMoneyIntervalField(
        u'Income Contribution Order',
        description=(
            u"Money you and/or your partner pay towards your criminal legal "
            u"aid"))
    childcare = PartnerMoneyIntervalField(
        u'Childcare',
        description=(
            u"Money you and your partner pay for your child to be looked "
            u"after while you work or study"))


class ApplicationForm(Form):
    title = StringField(
        u'Title',
        description=u"Mr, Mrs, Ms",
        validators=[InputRequired()])
    full_name = StringField(
        u'Full name',
        validators=[InputRequired()])
    contact_number = StringField(
        u'Contact phone number',
        validators=[InputRequired()])
    post_code = StringField(u'Postcode')
    address = TextAreaField(u'Address')
    extra_notes = TextAreaField(
        u'Help the operator to understand your situation',
        description=(
            u"In your own words, please tell us exactly what your problem is "
            u"about. The Civil Legal Advice operator will read this before "
            u"they call you."))
