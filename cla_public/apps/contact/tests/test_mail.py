import datetime
import logging
import unittest

from mock import ANY, MagicMock

from flask import session
from werkzeug.datastructures import MultiDict

from cla_public.app import create_app
from cla_public.apps.contact.views import create_and_send_confirmation_email
from cla_public.apps.contact.forms import ContactForm
from cla_public.config.common import GOVUK_NOTIFY_TEMPLATES

logging.getLogger("MARKDOWN").setLevel(logging.WARNING)


def submit(**kwargs):
    data = {
        "full_name": "John Smith",
        "email": "john.smith@example.com",
        "contact_type": "callback",
        "callback-contact_number": "0123456789",
        "thirdparty-full_name": "John Smith",
        "thirdparty-contact_number": "0123456789",
        "callback_requested": True,
    }

    if datetime.datetime.now().time() > datetime.time(hour=14, minute=30):
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
    else:
        data.update({"callback-time-specific_day": "today", "callback-time-time_today": "0900"})

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

    def email_args(self, **kwargs):
        arg_data = {"personalisation": ANY, "email_address": ANY, "template_id": ANY}
        arg_data.update(kwargs)
        return arg_data

    def test_confirmation_email_callback(self):
        govuk_notify = MagicMock()
        form = submit_and_store_in_session()
        create_and_send_confirmation_email(govuk_notify, form.data)
        govuk_notify.send_email.assert_called_with(
            self.email_args(template_id=GOVUK_NOTIFY_TEMPLATES["PUBLIC_CALLBACK_WITH_NUMBER"])
        )

    def test_confirmation_email_no_callback(self):
        govuk_notify = MagicMock()
        form = submit_and_store_in_session(callback_requested=False)
        create_and_send_confirmation_email(govuk_notify, form.data)
        govuk_notify.send_email.assert_called_with(
            self.email_args(template_id=GOVUK_NOTIFY_TEMPLATES["PUBLIC_CALLBACK_NOT_REQUESTED"])
        )

    def test_confirmation_email_thirdparty(self):
        govuk_notify = MagicMock()
        form = submit_and_store_in_session(contact_type="nothing", thirdparty=True)
        create_and_send_confirmation_email(govuk_notify, form.data)
        govuk_notify.send_email.assert_called_with(
            self.email_args(template_id=GOVUK_NOTIFY_TEMPLATES["PUBLIC_CALLBACK_THIRD_PARTY"])
        )
