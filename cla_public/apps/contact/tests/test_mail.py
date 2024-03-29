import datetime
import unittest

from mock import ANY, MagicMock

from flask import session
from werkzeug.datastructures import MultiDict

from cla_public.app import create_app
from cla_public.apps.contact.views import create_and_send_confirmation_email, set_callback_time_string
from cla_public.apps.contact.forms import ContactForm
from cla_public.config.common import GOVUK_NOTIFY_TEMPLATES
from cla_public.libs.utils import get_locale


def submit(**kwargs):
    data = {
        "full_name": "John Smith",
        "email": "john.smith@example.com",
        "contact_type": "callback",
        "callback-contact_number": kwargs.get("callback_contact_number", ""),
        "thirdparty-full_name": "John Smith",
        "thirdparty-contact_number": kwargs.get("thirdparty_contact_number", ""),
    }

    # use tomorrow because no more callbacks available today
    another_day = datetime.date.today() + datetime.timedelta(days=1)
    if another_day.weekday() in (5, 6):
        # use monday or tuesday next week to avoid weekend
        another_day += datetime.timedelta(days=2)
    data.update(
        {
            "callback-time-specific_day": "specific_day",
            "callback-time-day": "%04d%02d%02d" % (another_day.year, another_day.month, another_day.day),
            "callback-time-time_in_day": "0900",
        }
    )

    data.update(kwargs)
    return ContactForm(MultiDict(data), csrf_enabled=False)


def submit_and_store_in_session(**kwargs):
    form = submit(**kwargs)
    session.checker["ContactForm"] = form.data
    session.store_checker_details()
    return form


class TestConfirmationEmail(unittest.TestCase):
    def setUp(self):
        self.app = create_app("config/testing.py")
        self.ctx = self.app.test_request_context()
        self.ctx.push()
        self.client = self.app.test_client()
        session.checker["case_ref"] = "XX-XXXX-XXXX"

    def tearDown(self):
        self.ctx.pop()

    def assert_email_arguments(self, govuk_notify, template_id, personalisation=None):
        govuk_notify.send_email.assert_called_with(
            personalisation=personalisation if personalisation else ANY, email_address=ANY, template_id=template_id
        )

    def test_confirmation_email_callback(self):
        govuk_notify = MagicMock()
        form = submit_and_store_in_session(callback_contact_number="0123456789")
        session.stored["callback_requested"] = True
        create_and_send_confirmation_email(govuk_notify, form.data)
        date_time = set_callback_time_string(form.data)
        personalisation_data = {
            "date_time": date_time,
            "contact_number": "0123456789",
            "case_reference": "XX-XXXX-XXXX",
            "full_name": "John Smith",
            "thirdparty_full_name": "John Smith",
        }
        self.assert_email_arguments(
            govuk_notify,
            personalisation=personalisation_data,
            template_id=GOVUK_NOTIFY_TEMPLATES["PUBLIC_CALLBACK_WITH_NUMBER"][get_locale()[:2]],
        )

    def test_confirmation_email_no_callback(self):
        govuk_notify = MagicMock()
        form = submit_and_store_in_session(contact_type="nothing")
        session.stored["callback_requested"] = False
        create_and_send_confirmation_email(govuk_notify, form.data)
        date_time = set_callback_time_string(form.data)
        personalisation_data = {
            "date_time": date_time,
            "case_reference": "XX-XXXX-XXXX",
            "full_name": "John Smith",
            "thirdparty_full_name": "John Smith",
        }
        self.assert_email_arguments(
            govuk_notify,
            personalisation=personalisation_data,
            template_id=GOVUK_NOTIFY_TEMPLATES["PUBLIC_CALLBACK_NOT_REQUESTED"][get_locale()[:2]],
        )

    def test_confirmation_email_thirdparty(self):
        govuk_notify = MagicMock()
        form = submit_and_store_in_session(thirdparty_contact_number="0123456789")
        session.stored["callback_requested"] = True
        create_and_send_confirmation_email(govuk_notify, form.data)
        date_time = set_callback_time_string(form.data)
        personalisation_data = {
            "date_time": date_time,
            "contact_number": "0123456789",
            "case_reference": "XX-XXXX-XXXX",
            "full_name": "John Smith",
            "thirdparty_full_name": "John Smith",
        }
        self.assert_email_arguments(
            govuk_notify,
            personalisation=personalisation_data,
            template_id=GOVUK_NOTIFY_TEMPLATES["PUBLIC_CALLBACK_THIRD_PARTY"][get_locale()[:2]],
        )

    def test_confirmation_no_callback(self):
        govuk_notify = MagicMock()
        form = submit_and_store_in_session()
        dictform = form.data
        dictform.pop("full_name")
        session.stored["callback_requested"] = False
        create_and_send_confirmation_email(govuk_notify, dictform)
        personalisation_data = {"case_reference": "XX-XXXX-XXXX"}
        self.assert_email_arguments(
            govuk_notify,
            personalisation=personalisation_data,
            template_id=GOVUK_NOTIFY_TEMPLATES["PUBLIC_CONFIRMATION_NO_CALLBACK"][get_locale()[:2]],
        )

    def test_confirmation_callback(self):
        govuk_notify = MagicMock()
        form = submit_and_store_in_session()
        dictform = form.data
        dictform.pop("full_name")
        session.stored["callback_requested"] = True
        create_and_send_confirmation_email(govuk_notify, dictform)
        date_time = set_callback_time_string(form.data)
        personalisation_data = {"date_time": date_time, "case_reference": "XX-XXXX-XXXX"}
        self.assert_email_arguments(
            govuk_notify,
            personalisation=personalisation_data,
            template_id=GOVUK_NOTIFY_TEMPLATES["PUBLIC_CONFIRMATION_EMAIL_CALLBACK_REQUESTED"][get_locale()[:2]],
        )


class TestSetCallbackTimeString(unittest.TestCase):
    def test_set_callback_time_string(self):
        session.stored["callback_requested"] = True
        session.stored["callback_time"] = datetime.datetime(2023, 5, 19, 9, 0)
        date_time = set_callback_time_string(data={})
        self.assertEqual(date_time, "Friday, 19 May at 09:00 - 09:30")
