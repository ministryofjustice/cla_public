# coding: utf-8
from mock import Mock
import unittest

from werkzeug.datastructures import MultiDict
from wtforms import Form
from wtforms.validators import StopValidation, ValidationError

from cla_public import app
from cla_public.apps.checker.constants import MONEY_INTERVALS
from cla_public.apps.checker.fields import MoneyIntervalField
from cla_public.apps.checker.validators import MoneyIntervalAmountRequired, ValidMoneyInterval


def test_form(**kwargs):
    class TestForm(Form):
        money_interval = MoneyIntervalField(**kwargs)

        @classmethod
        def submit(cls, data):
            return cls(MultiDict(data))

    return TestForm


class TestMoneyInterval(unittest.TestCase):
    def setUp(self):
        self.app = app.create_app("config/testing.py")
        self.app = self.app.test_client()
        self.validator = None

    def assertValidationError(self, form, field):
        with self.assertRaises(ValidationError):
            self.validator(form, field)

    def assertStopValidationError(self, form, field):
        with self.assertRaises(StopValidation):
            self.validator(form, field)

    def assertValidationPasses(self, form, field, message=None):
        try:
            self.validator(form, field)
        except ValidationError as e:
            if message is None:
                message = str(e)
            self.fail(message)

    def test_money_interval_validator_not_completed(self):
        self.validator = ValidMoneyInterval()
        form = Mock()
        field = Mock()
        field.form.per_interval_value.data = None
        field.form.per_interval_value.errors = []
        field.form.interval_period.data = ""
        self.assertValidationPasses(form, field)

    def test_money_interval_validator_invalid_amount(self):
        self.validator = ValidMoneyInterval()
        form = Mock()
        field = Mock()
        field.form.per_interval_value.errors = ["Invalid amount"]
        self.assertValidationError(form, field)

    def test_money_interval_validator_amount_not_set_interval_selected(self):
        self.validator = ValidMoneyInterval()
        form = Mock()
        field = Mock()
        field.form.per_interval_value.data = None
        field.form.per_interval_value.errors = []
        field.form.interval_period.data = "per_week"
        self.assertValidationError(form, field)

    def test_money_interval_validator_amount_set_interval_not_selected(self):
        self.validator = ValidMoneyInterval()
        form = Mock()
        field = Mock()
        field.form.per_interval_value.data = 100
        field.form.per_interval_value.errors = []
        field.form.interval_period.data = ""
        self.assertValidationError(form, field)

        field.form.per_interval_value.data = 0
        self.assertValidationPasses(form, field)

    def test_money_interval_validator_amount_set_interval_selected(self):
        self.validator = ValidMoneyInterval()
        form = Mock()
        field = Mock()
        field.form.per_interval_value.data = 100

        for interval, _ in MONEY_INTERVALS:
            if interval != "":
                field.form.interval_period.data = interval
                field.form.per_interval_value.errors = []
                self.assertValidationPasses(form, field)

    def test_money_interval_amount_required(self):
        self.validator = MoneyIntervalAmountRequired()
        form = Mock()
        field = Mock()
        field.form.per_interval_value.data = None
        field.form.per_interval_value.errors = []
        self.assertStopValidationError(form, field)

    def test_money_interval_max_val(self):
        form = test_form().submit(
            {"money_interval-per_interval_value": "100,000,000.00", "money_interval-interval_period": "per_week"}
        )
        form.validate()

        self.assertIn(u"This amount must be less than £100,000,000", form.money_interval.errors)

    def test_money_interval_only_one_error_if_amount_missing(self):
        form = test_form(validators=[MoneyIntervalAmountRequired()]).submit(
            {"money_interval-per_interval_value": "", "money_interval-interval_period": "per_week"}
        )
        form.validate()
        self.assertIn(u"Please provide an amount", form.money_interval.errors)
        self.assertEqual(1, len(form.money_interval.errors))
