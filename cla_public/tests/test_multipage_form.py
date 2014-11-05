from __future__ import unicode_literals

from flask import url_for
from cla_public import app
from cla_public.apps.checker.forms import (set_form_session_key,
                                           unset_form_session_key,
                                           get_form_session_key)
import unittest


class TestMultiPageForm(unittest.TestCase):

    def setUp(self):
        self.app = app.create_app('FLASK_TEST')
        self._ctx = self.app.test_request_context()
        self._ctx.push()

    def tearDown(self):
        pass

    def test_session_set_and_unset(self):
        # Test that we can set, unset and recall session state.
        set_form_session_key('test_key', 'test_value')
        self.assertEqual(get_form_session_key('test_key'), 'test_value')
        unset_form_session_key('test_key')
        with self.assertRaises(KeyError):
            get_form_session_key('test_key')

    def test_session_single_page_valid_form(self):
        # Test that POSTing to a single page will store the form data
        # against the session.
        with self.app.test_client() as c:
            uri = url_for('checker.problem')
            choice = 'debt'
            resp = c.post(uri, data={'categories': choice})
            # We expect a 302 redirect as we are shuffled to the next
            # page.
            self.assertEquals(resp.status_code, 302)
            # The session store should now contain a field called
            # <FormName>_categories where FormName is ProblemForm.
            key = '{0}_{1}'.format('ProblemForm', 'categories')
            self.assertEquals(get_form_session_key(key), choice)

    def test_session_single_page_fail_validation(self):
        # Test that POSTing to a single page -- and fail the form
        # validation requirements
        with self.app.test_client() as c:
            # POST correct details
            uri = url_for('checker.problem')
            # Make an invalid choice
            choice = None
            resp = c.post(uri, data={'categories': choice})
            # Get a 200 OK because we are re-sending the original
            # Problem page.
            self.assertEquals(resp.status_code, 200)

            # Test that the "categories" field is not stored in the
            # session.
            with self.assertRaises(KeyError):
                key = '{0}_{1}'.format('ProblemForm', 'categories')
                get_form_session_key(key)
