from mock import Mock
import unittest

from wtforms.validators import StopValidation, ValidationError

from cla_public import app
from cla_public.apps.checker.constants import MONEY_INTERVALS
from cla_public.apps.checker.validators import MoneyIntervalAmountRequired, ValidMoneyInterval


class TestMoneyInterval(unittest.TestCase):

    def setUp(self):
        self.app = app.create_app('config/testing.py')
        self.app = self.app.test_client()
        self.validator = None

    def assertValidationError(self, form, field):
        with self.assertRaises(ValidationError):
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
        field.form.interval_period.data = ''
        self.assertValidationPasses(form, field)

    def test_money_interval_validator_invalid_amount(self):
        self.validator = ValidMoneyInterval()
        form = Mock()
        field = Mock()
        field.form.per_interval_value.validate = Mock(side_effect=ValidationError())
        self.assertValidationError(form, field)

    def test_money_interval_validator_amount_not_set_interval_selected(self):
        self.validator = ValidMoneyInterval()
        form = Mock()
        field = Mock()
        field.form.per_interval_value.data = None
        field.form.interval_period.data = 'per_week'
        self.assertValidationError(form, field)

    def test_money_interval_validator_amount_set_interval_not_selected(self):
        self.validator = ValidMoneyInterval()
        form = Mock()
        field = Mock()
        field.form.per_interval_value.data = 100
        field.form.interval_period.data = ''
        self.assertValidationError(form, field)

        field.form.per_interval_value.data = 0
        self.assertValidationPasses(form, field)

    def test_money_interval_validator_amount_set_interval_selected(self):
        self.validator = ValidMoneyInterval()
        form = Mock()
        field = Mock()
        field.form.per_interval_value.data = 100

        for interval, _ in MONEY_INTERVALS:
            if interval != '':
                field.form.interval_period.data = interval
                self.assertValidationPasses(form, field)

    def test_money_interval_amount_required(self):
        self.validator = MoneyIntervalAmountRequired()
        form = Mock()
        field = Mock()
        field.form.per_interval_value.data = None
        self.assertValidationError(form, field)
