import datetime
import logging
import unittest

from flask import session
from werkzeug.datastructures import MultiDict

from cla_public.app import create_app
from cla_public.apps.contact.views import create_confirmation_email
from cla_public.apps.contact.forms import ContactForm


logging.getLogger("MARKDOWN").setLevel(logging.WARNING)


def submit(**kwargs):
    data = {
        "full_name": "John Smith",
        "email": "john.smith@example.com",
        "contact_type": "callback",
        "callback-contact_number": "0123456789",
        "callback-safe_to_contact": "SAFE",
    }

    if datetime.datetime.now().time() > datetime.time(hour=17, minute=30):
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


class TestMail(unittest.TestCase):
    def setUp(self):
        self.app = create_app("config/testing.py")
        self.ctx = self.app.test_request_context()
        self.ctx.push()
        self.client = self.app.test_client()
        session.checker["case_ref"] = "XX-XXXX-XXXX"

    def tearDown(self):
        self.ctx.pop()

    def receive_email(self, msg):
        with self.app.mail.record_messages() as outbox:
            self.app.mail.send(msg)
            assert len(outbox) == 1
            return outbox[0]

    def test_confirmation_email(self):
        with self.client:
            form = submit_and_store_in_session()
            msg = create_confirmation_email(form.data)
            msg = self.receive_email(msg)

            assert msg.subject == "Your Civil Legal Advice reference number"
            assert "Dear John Smith" in msg.body
            assert "reference number is XX-XXXX-XXXX" in msg.body
            assert "call you back on 0123456789" in msg.body
            callback_time = form.data["callback"]["time"]
            self.assertIn(
                "during your chosen time ({0:%A, %d %B at %H:%M} - {1:%H:%M})".format(
                    callback_time, callback_time + datetime.timedelta(minutes=30)
                ),
                msg.body,
            )
            assert "We will leave a message" in msg.body

    def test_confirmation_email_not_safe(self):
        with self.client:
            form = submit_and_store_in_session(**{"callback-safe_to_contact": "NO_MESSAGE"})
            msg = create_confirmation_email(form.data)
            msg = self.receive_email(msg)

            assert "We will not leave a message" in msg.body

    def test_confirmation_email_no_callback(self):
        with self.client:
            form = submit_and_store_in_session(contact_type="call")
            msg = create_confirmation_email(form.data)
            msg = self.receive_email(msg)

            assert "reference number is XX-XXXX-XXXX" in msg.body
            assert "You can now call CLA" in msg.body
