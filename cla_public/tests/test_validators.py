from __future__ import unicode_literals
import unittest
from mock import MagicMock

from flask import url_for, session
from wtforms.validators import ValidationError
from cla_public import app
from cla_public.apps.checker.fields import ZeroOrNoneValidator

def make_key(form, field):
    return '{form}_{field}'.format(form=form, field=field)


class TestMultiPageForm(unittest.TestCase):

    def setUp(self):
        self.app = app.create_app('FLASK_TEST')
        self._ctx = self.app.test_request_context()
        self._ctx.push()

    def tearDown(self):
        pass

    def test_ZeroOrNoneValidator_no_data(self):

        form = MagicMock()
        field = MagicMock()
        field.data = None
        v = ZeroOrNoneValidator(min_val=0, max_val=100)
        # Call validator. It will return None if the validator passed.
        return_val = v(form, field)
        self.assertIsNone(return_val)

    def test_ZeroOrNoneValidator_has_min_value(self):

        form = MagicMock()
        field = MagicMock()

        actual_value = 0
        field.data = actual_value
        v = ZeroOrNoneValidator(min_val=0, max_val=100)
        # Call validator. It will return None if the validator passed.
        return_val = v(form, field)
        self.assertIsNone(return_val)

    def test_ZeroOrNoneValidator_fails_min_value(self):

        form = MagicMock()
        field = MagicMock()

        actual_value = -1
        field.data = actual_value
        v = ZeroOrNoneValidator(min_val=0, max_val=100)
        # Call validator. It will return an exception as we fail the
        # check because -1 is less tha min_val.
        with self.assertRaises(ValidationError):
            return_val = v(form, field)

    def test_ZeroOrNoneValidator_fails_max_value(self):

        form = MagicMock()
        field = MagicMock()

        actual_value = 1000
        field.data = actual_value
        v = ZeroOrNoneValidator(min_val=0, max_val=100)
        # Call validator. It will return an exception as we fail the
        # check because -1 is less tha min_val.
        with self.assertRaises(ValidationError):
            return_val = v(form, field)

