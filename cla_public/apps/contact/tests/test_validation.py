import datetime
import logging
import unittest

from werkzeug.datastructures import MultiDict
from cla_public.app import create_app
from cla_public.apps.contact.forms import CallBackForm
from cla_public.apps.contact.tests.test_availability import override_current_time
from cla_public.apps.contact.constants import (
    TIME_TODAY_VALIDATION_ERROR,
    DAY_SPECIFIC_VALIDATION_ERROR,
    TIME_SPECIFIC_VALIDATION_ERROR,
)

logging.getLogger("MARKDOWN").setLevel(logging.WARNING)


def base_form_data():
    data = {"contact_number": "000000000", "time-specific_day": "today", "time-time_today": "1400"}

    return data


def validate_contact_form(data):
    form = CallBackForm(MultiDict(data), csrf_enabled=False)
    valid_submit = form.validate()
    return valid_submit, form.errors.get("time", {})


class TestContactFormValidation(unittest.TestCase):
    def setUp(self):
        self.app = create_app("config/testing.py")
        self.ctx = self.app.test_request_context()
        self.ctx.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.ctx.pop()

    def test_valid_callback_another_day(self):
        with self.client:
            # fix day, date and time as 9am Thursday Dec 8 22
            with override_current_time(datetime.datetime(2022, 12, 8, 9, 00)):
                data = {
                    "time-specific_day": "specific_day",
                    "time-day": "%04d%02d%02d" % (2022, 12, 9),
                    "time-time_in_day": "0900",
                    "contact_number": "000000000",
                }
                # should be valid
                is_valid, errors = validate_contact_form(data)
                self.assertTrue(is_valid)

    def test_valid_callback_today(self):
        with self.client:
            # fix day, date and time as 9am Thursday Dec 8 22
            with override_current_time(datetime.datetime(2022, 12, 8, 9, 00)):
                data = {"time-specific_day": "today", "time-time_today": "1400", "contact_number": "000000000"}
                is_valid, errors = validate_contact_form(data)
                self.assertTrue(is_valid)

    def test_callback_no_specific_day_set(self):
        with self.client:
            # fix day, date and time as 9am Thursday Dec 8 22
            with override_current_time(datetime.datetime(2022, 12, 8, 9, 00)):
                data = {
                    "time-specific_day": "specific_day",
                    "time-day": "",
                    "time-time_in_day": "0900",
                    "contact_number": "000000000",
                }
                is_valid, errors = validate_contact_form(data)
                if not is_valid:
                    # check the errors
                    self.assertIn(DAY_SPECIFIC_VALIDATION_ERROR, errors["day"][0])
                    self.assertIn("schedule a callback at the requested time", errors["time_in_day"][0][0])
                else:
                    self.fail("Specific day was not set but form was validated")

    def test_callback_no_time_today_set(self):
        with self.client:
            # fix day, date and time as 9am Thursday Dec 8 22
            with override_current_time(datetime.datetime(2022, 12, 8, 9, 00)):
                data = {"time-specific_day": "today", "time-time_in_day": "", "contact_number": "000000000"}
                is_valid, errors = validate_contact_form(data)
                if not is_valid:
                    # check the errors
                    self.assertIn(TIME_TODAY_VALIDATION_ERROR, errors["time_today"][0])
                else:
                    self.fail("Time today was not set but form was validated")

    def test_callback_no_time_specific_day_set(self):
        with self.client:
            # fix day, date and time as 9am Thursday Dec 8 22
            with override_current_time(datetime.datetime(2022, 12, 8, 9, 00)):
                data = {
                    "time-specific_day": "specific_day",
                    "time-day": "%04d%02d%02d" % (2022, 12, 9),
                    "time-time_in_day": "",
                    "contact_number": "000000000",
                }
                is_valid, errors = validate_contact_form(data)
                if not is_valid:
                    # check the errors
                    self.assertIn(TIME_SPECIFIC_VALIDATION_ERROR, errors["time_in_day"][0])
                else:
                    self.fail("Specific day was not set but form was validated")
