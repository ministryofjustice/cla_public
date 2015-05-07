import datetime
import logging
import unittest

from flask import session

from cla_public.app import create_app
from cla_public.apps.checker.constants import NO, YES
from cla_public.apps.contact.views import confirmation_email


logging.getLogger('MARKDOWN').setLevel(logging.WARNING)


class TestMail(unittest.TestCase):

    def setUp(self):
        self.app = create_app('config/testing.py')
        self.ctx = self.app.test_request_context()
        self.ctx.push()
        self.client = self.app.test_client()
        session.checker['case_ref'] = 'XX-XXXX-XXXX'

        self.form_data = {
            'full_name': 'John Smith',
            'email': 'john.smith@example.com',
            'callback_requested': YES,
            'contact_number': '0123456789',
            'safe_to_contact': YES,
            'callback_time': datetime.datetime(2015, 5, 7, 11, 30)}

    def tearDown(self):
        self.ctx.pop()

    def receive_email(self, msg):
        with self.app.mail.record_messages() as outbox:
            self.app.mail.send(msg)
            assert len(outbox) == 1
            return outbox[0]

    def test_confirmation_email(self):
        with self.client:
            data = self.form_data
            msg = confirmation_email(data)
            msg = self.receive_email(msg)

            assert msg.subject == 'Your Civil Legal Advice reference number'
            assert 'Dear John Smith' in msg.body
            assert 'reference number is XX-XXXX-XXXX' in msg.body
            assert 'call you back on 0123456789' in msg.body
            assert 'time you selected ({0:%A, %d %B at %H:%M})'.format(
                data['callback_time']) in msg.body
            assert 'We will leave a message' in msg.body

    def test_confirmation_email_not_safe(self):
        with self.client:
            data = self.form_data
            data['safe_to_contact'] = NO
            msg = confirmation_email(data)
            msg = self.receive_email(msg)

            assert 'We will not leave a message' in msg.body

    def test_confirmation_email_no_callback(self):
        with self.client:
            data = self.form_data
            data['callback_requested'] = NO
            msg = confirmation_email(data)
            msg = self.receive_email(msg)

            assert 'reference number is XX-XXXX-XXXX' in msg.body
            assert 'You can now call CLA' in msg.body
