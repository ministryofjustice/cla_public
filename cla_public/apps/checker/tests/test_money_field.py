# coding: utf-8
import unittest

from werkzeug.datastructures import MultiDict
from wtforms import Form
from wtforms.validators import Optional

from cla_public.apps.checker.fields import MoneyField


class TestForm(Form):
    default_moneyfield = MoneyField(validators=[Optional])
    max_val_moneyfield = MoneyField(max_val=500, validators=[Optional])
    no_min_moneyfield = MoneyField(min_val=None, validators=[Optional])


def submit(**kwargs):
    return TestForm(MultiDict(kwargs))


class TestMoneyField(unittest.TestCase):

    def assertAmount(self, expected, amount, field='default_moneyfield'):
        form = submit(**{field: amount})
        actual = getattr(form, field).data
        if actual != expected:
            self.fail((
                'Expected sanitized amount {0} for input {1}, '
                'but got {2}').format(expected, amount, actual))

    def assertInvalidAmount(self, amount):
        form = submit(default_moneyfield=amount)
        self.assertIn(
            u'Not a valid amount',
            form.default_moneyfield.process_errors,
            '{0} is a valid amount'.format(amount))

    def assertValidAmount(self, amount):
        form = submit(default_moneyfield=amount)
        self.assertNotIn(
            u'Not a valid amount',
            form.default_moneyfield.process_errors,
            '{0} is an invalid amount'.format(amount))

    def assertAmountTooLow(self, amount):
        form = submit(default_moneyfield=amount)
        self.assertIn(
            u'This amount must be more than £0',
            form.default_moneyfield.process_errors,
            '{0} is not too low'.format(amount))

    def assertAmountTooHigh(self, amount, field='max_val_moneyfield'):
        form = submit(**{field: amount})
        max_val = getattr(form, field).max_val / 100.0
        self.assertIn(
            u'This amount must be less than £{:,.0f}'.format(max_val),
            getattr(form, field).process_errors,
            '{0} is not too high'.format(amount))

    def test_integer(self):
        self.assertValidAmount('500')
        self.assertAmount(50000, '500')

    def test_decimal(self):
        self.assertValidAmount('10.5')
        self.assertAmount(1050, '10.5')

    def test_amount(self):
        self.assertValidAmount('12.34')
        self.assertAmount(1234, '12.34')

    def test_too_many_decimal_places(self):
        self.assertInvalidAmount('12.345')

    def test_not_a_number(self):
        self.assertInvalidAmount('abc')
        self.assertInvalidAmount('1twothree')
        self.assertInvalidAmount('one2three')

    def test_ignore_commas_and_spaces(self):
        self.assertValidAmount('1,200')
        self.assertAmount(120000, '1,200')
        self.assertValidAmount('1,,,,2')
        self.assertAmount(1200, '1,,,,2')
        self.assertValidAmount('  1  3  ')
        self.assertAmount(1300, '  1  3  ')
        self.assertValidAmount('12, 34, 56')
        self.assertAmount(12345600, '12, 34, 56')
        self.assertValidAmount('123.4      ')
        self.assertAmount(12340, '123.4      ')

    def test_only_one_decimal_point(self):
        self.assertInvalidAmount('1.23.45')
        self.assertInvalidAmount('12.3 45.6')

    def test_no_commas_or_spaces_in_pence(self):
        self.assertInvalidAmount('123.4,6')
        self.assertInvalidAmount('123.4 6')

    def test_negative_amounts_ok(self):
        self.assertValidAmount('-32')
        self.assertAmount(-3200, '-32', field='no_min_moneyfield')

    def test_below_min_val(self):
        self.assertValidAmount('-32')
        self.assertAmountTooLow('-32')
        self.assertValidAmount('-12.34')
        self.assertAmountTooLow('-12.34')

    def test_above_max_val(self):
        self.assertAmountTooHigh('600')

    def test_default_max(self):
        self.assertAmountTooHigh('100000000.00', field='default_moneyfield')
