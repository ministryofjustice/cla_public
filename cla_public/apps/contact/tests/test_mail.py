import datetime
import logging
import unittest

from flask import session
from werkzeug.datastructures import MultiDict

from cla_public.app import create_app
from cla_public.apps.contact.views import confirmation_email
from cla_public.apps.contact.forms import ContactForm


logging.getLogger('MARKDOWN').setLevel(logging.WARNING)


def submit(**kwargs):
    data = {
        'full_name': 'John Smith',
        'email': 'john.smith@example.com',
        'contact_type': 'callback',
        'callback-contact_number': '0123456789',
        'time_today': '1130',
        'specific_day': 'today',
        'callback-safe_to_contact': 'SAFE'}
    data.update(kwargs)
    return ContactForm(MultiDict(data), csrf_enabled=False)


class TestMail(unittest.TestCase):

    def setUp(self):
        self.app = create_app('config/testing.py')
        self.ctx = self.app.test_request_context()
        self.ctx.push()
        self.client = self.app.test_client()
        session.checker['case_ref'] = 'XX-XXXX-XXXX'

    def tearDown(self):
        self.ctx.pop()

    def receive_email(self, msg):
        with self.app.mail.record_messages() as outbox:
            self.app.mail.send(msg)
            assert len(outbox) == 1
            return outbox[0]

    def test_confirmation_email(self):
        with self.client:
            form = submit()
            msg = confirmation_email(form.data)
            msg = self.receive_email(msg)

            assert msg.subject == 'Your Civil Legal Advice reference number'
            assert 'Dear John Smith' in msg.body
            assert 'reference number is XX-XXXX-XXXX' in msg.body
            assert 'call you back on 0123456789' in msg.body
            assert 'time you selected ({0:%A, %d %B at %H:%M})'.format(
                form.data['callback']['time']) in msg.body
            assert 'We will leave a message' in msg.body

    def test_confirmation_email_not_safe(self):
        with self.client:
            form = submit(**{'callback-safe_to_contact': 'NO_MESSAGE'})
            msg = confirmation_email(form.data)
            msg = self.receive_email(msg)

            assert 'We will not leave a message' in msg.body

    def test_confirmation_email_no_callback(self):
        with self.client:
            form = submit(contact_type='call')
            msg = confirmation_email(form.data)
            msg = self.receive_email(msg)

            assert 'reference number is XX-XXXX-XXXX' in msg.body
            assert 'You can now call CLA' in msg.body
