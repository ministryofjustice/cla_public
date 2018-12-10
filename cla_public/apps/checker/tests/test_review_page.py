from collections import defaultdict
import logging
import unittest

from bs4 import BeautifulSoup

from cla_public.app import create_app
from cla_public.apps.checker.constants import YES, NO


logging.getLogger('MARKDOWN').setLevel(logging.WARNING)


class TestReviewPage(unittest.TestCase):

    def setUp(self):
        app = create_app('config/testing.py')
        self.client = app.test_client()
        self._html = None
        self._last_session = None

    @property
    def review_page_html(self):
        with self.client.session_transaction() as session:
            if self._html is None or session != self._last_session:
                self._html = self.client.get('/review').data
                self._last_session = session
        return self._html

    def assert_review_section(self, url):
        soup = BeautifulSoup(self.review_page_html, features="html.parser")
        section = next(
            iter(soup.select('section header a[href="{0}"]'.format(url))),
            None)
        self.assertIsNotNone(
            section,
            'Section not present: {0}'.format(url))

    def find_question(self, question):
        soup = BeautifulSoup(self.review_page_html, features="html.parser")
        return next(iter(soup.find_all('th', {'data-field': question})), None)

    def assert_answer_shown(self, question):
        self.assertIsNotNone(
            self.find_question(question),
            '"{0}" is not shown'.format(question))

    def assert_answer_not_shown(self, question):
        self.assertIsNone(
            self.find_question(question),
            '"{0}" is shown'.format(question))

    def set_problem(self, problem):
        with self.client.session_transaction() as session:
            session.checker['category'] = problem

    def set_about_you_answers(self, **kwargs):
        answers = defaultdict(lambda: NO)
        answers.update(kwargs)
        answers.update({
            'is_completed': True
        })
        with self.client.session_transaction() as session:
            session.checker['AboutYouForm'] = answers

    def set_benefits(self, passported=None, *benefits):
        if passported is True:
            benefits = ['income_support']
        elif passported is False:
            benefits = ['other-benefit']
        with self.client.session_transaction() as session:
            session.checker['YourBenefitsForm'] = {
                'benefits': benefits,
                'is_completed': True}

    def set_additional_benefits_answers(self, **answers):
        answers.update({
            'is_completed': True
        })
        with self.client.session_transaction() as session:
            session.checker['AdditionalBenefitsForm'] = answers

    def test_review_page_about_you(self):
        self.set_problem('debt')
        self.set_about_you_answers(on_benefits=YES)
        self.set_benefits(passported=False)
        self.assert_review_section('/about')

    def test_bug_passported_about_you_missing(self):
        self.set_problem('debt')
        self.set_about_you_answers(on_benefits=YES)
        self.set_benefits(passported=True)
        self.assert_review_section('/about')

    def test_null_default_values_shown(self):
        self.set_problem('debt')
        self.set_about_you_answers(on_benefits=YES)
        self.set_benefits(passported=False)
        self.set_additional_benefits_answers(other_benefits=NO)
        self.assert_answer_not_shown('total_other_benefit')

    def test_children_not_shown_after_deselected(self):
        self.set_problem('debt')
        self.set_about_you_answers(have_children=NO, num_children=1)
        self.assert_answer_not_shown('num_children')
