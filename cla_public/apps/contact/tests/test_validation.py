# -*- coding: utf-8 -*-
import datetime
import logging
import unittest

from werkzeug.datastructures import MultiDict
from cla_public.app import create_app
from cla_public.apps.contact.forms import CallBackForm, ContactForm
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


def validate_contact_form(data, form_var):
    form = CallBackForm(MultiDict(data), csrf_enabled=True)
    valid_submit = form.validate()
    return valid_submit, form.errors.get(form_var, {})


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
                    "announce_call_from_cla": "true",
                }
                # should be valid
                is_valid, errors = validate_contact_form(data, "time")
                self.assertTrue(is_valid)

    def test_valid_callback_today(self):
        with self.client:
            # fix day, date and time as 9am Thursday Dec 8 22
            with override_current_time(datetime.datetime(2022, 12, 8, 9, 00)):
                data = {
                    "time-specific_day": "today",
                    "time-time_today": "1400",
                    "contact_number": "000000000",
                    "announce_call_from_cla": "true",
                }
                is_valid, errors = validate_contact_form(data, "time")
                self.assertTrue(is_valid)

    def test_valid_no_announce_call_from_cla_selected(self):
        with self.client:
            # fix day, date and time as 9am Thursday Dec 8 22
            with override_current_time(datetime.datetime(2022, 12, 8, 9, 00)):
                data = {
                    "time-specific_day": "today",
                    "time-time_today": "1400",
                    "contact_number": "000000000",
                    "announce_call_from_cla": "",
                }
                is_valid, errors = validate_contact_form(data, "announce_call_from_cla")
                if not is_valid:
                    # check the errors
                    self.assertIn(u"Select if we can say that we’re calling from Civil Legal Advice", errors[0])
                else:
                    self.fail("Announce call from cla was not set but form was validated")

    def test_callback_no_specific_day_set(self):
        with self.client:
            # fix day, date and time as 9am Thursday Dec 8 22
            with override_current_time(datetime.datetime(2022, 12, 8, 9, 00)):
                data = {
                    "time-specific_day": "specific_day",
                    "time-day": "",
                    "time-time_in_day": "0900",
                    "contact_number": "000000000",
                    "announce_call_from_cla": "yes",
                }
                is_valid, errors = validate_contact_form(data, "time")
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
                is_valid, errors = validate_contact_form(data, "time")
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
                    "announce_call_from_cla": "yes",
                }
                is_valid, errors = validate_contact_form(data, "time")
                if not is_valid:
                    # check the errors
                    self.assertIn(TIME_SPECIFIC_VALIDATION_ERROR, errors["time_in_day"][0])
                else:
                    self.fail("Specific day was not set but form was validated")

    def test_bsl(self):
        with self.client:
            data = {
                "adaptations-other_language": "",
                "adaptations-bsl_webcam": "y",
                "email": "john.doe@digital.justice.gov.uk",
                "contact_type": "call",
                "full_name": "John Doe",
            }
            form = ContactForm(MultiDict(data), csrf_enabled=False)
            self.assertTrue(form.validate())
            self.assertEqual(form.api_payload()["personal_details"]["email"], "john.doe@digital.justice.gov.uk")

    def test_bsl_email_success(self):
        with self.client:
            data = {
                "adaptations-other_language": "",
                "adaptations-bsl_webcam": "y",
                "adaptations-bsl_email": "john.doe@digital.justice.gov.uk",
                "contact_type": "call",
                "full_name": "John Doe",
            }
            form = ContactForm(MultiDict(data), csrf_enabled=False)
            self.assertTrue(form.validate())
            self.assertEqual(form.api_payload()["personal_details"]["email"], "john.doe@digital.justice.gov.uk")

    def test_bsl_email_missing_email(self):
        with self.client:
            data = {
                "adaptations-other_language": "",
                "adaptations-bsl_webcam": "y",
                "contact_type": "call",
                "full_name": "John Doe",
            }
            form = ContactForm(MultiDict(data), csrf_enabled=False)
            self.assertFalse(form.validate())
            self.assertIn(
                ("bsl_email", ["Enter your email address so we can arrange a BSL call"]), form.errors["adaptations"]
            )
