from __future__ import unicode_literals
import unittest

from flask import url_for, session
from cla_public import app


def make_key(form, field):
    return '{form}.{field}'.format(form=form, field=field)


class TestMultiPageForm(unittest.TestCase):

    def setUp(self):
        self.app = app.create_app('FLASK_TEST')
        self._ctx = self.app.test_request_context()
        self._ctx.push()

    def tearDown(self):
        pass

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
            key = make_key('ProblemForm', 'categories')
            self.assertEquals(session.get(key), choice)

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
            key = make_key('ProblemForm', 'categories')
            self.assertFalse(key in session)

    def test_session_multi_page_valid_forms(self):
        # Test that Form fields are stored across several pages and
        # requests in the session object.

        def post_form_page(page_name, data):
            uri = url_for(page_name)
            resp = c.post(uri, data=data)
            # We expect a 302 redirect as we are shuffled to the next
            # page.
            self.assertEquals(resp.status_code, 302)

        with self.app.test_client() as c:
            problem_data = {'categories': 'debt'}
            post_form_page('checker.problem', problem_data)

            about_data = {
                'have_partner': '1',
                'in_dispute': '0',
                'on_benefits': '0',
                'have_children': '0',
                'num_children': 0,
                'have_dependants': '0',
                'num_dependants': 0,
                'have_savings': '0',
                'own_property': '0',
                'is_employed': '0',
                'is_self_employed': '0',
                'aged_60_or_over': '0',
                }

            post_form_page('checker.about', about_data)

            self.assertEqual(
                session.get(make_key('ProblemForm', 'categories')),
                problem_data['categories'])

            for field, value in about_data.items():
                self.assertEqual(
                    session.get(make_key('AboutYouForm', field)),
                    value)
