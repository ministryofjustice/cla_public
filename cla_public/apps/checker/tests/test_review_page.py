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

    def assertReviewSection(self, url, html):
        soup = BeautifulSoup(html)
        section = next(
            iter(soup.select('.main-content h2 a[href="{0}"]'.format(url))),
            None)
        self.assertIsNotNone(
            section,
            'Section not present: {0}'.format(url))

    def assertQuestionNotShown(self, question, html):
        soup = BeautifulSoup(html)
        questions = soup.find_all('th', {'data-field': question})
        self.assertIsNone(
            next(iter(questions), None),
            'Question "{0}" is shown'.format(question))

    def setProblem(self, problem):
        with self.client.session_transaction() as session:
            session['ProblemForm'] = {
                'categories': problem}

    def setAboutYouAnswers(self, **kwargs):
        answers = defaultdict(lambda: NO)
        answers.update(kwargs)
        with self.client.session_transaction() as session:
            session['AboutYouForm'] = answers

    def setBenefits(self, passported=None, *benefits):
        if passported is True:
            benefits = ['income_support']
        elif passported is False:
            benefits = ['other-benefit']
        with self.client.session_transaction() as session:
            session['YourBenefitsForm'] = {
                'benefits': benefits}

    def setBenefitsTaxCreditsAnswers(self, **answers):
        with self.client.session_transaction() as session:
            session['TaxCreditsForm'] = answers

    def test_review_page_about_you(self):
        self.setProblem('debt')
        self.setAboutYouAnswers(on_benefits=YES)
        self.setBenefits(passported=False)
        response = self.client.get('/review')
        self.assertReviewSection('/about', response.data)

    def test_review_page_bug_passported_about_you_missing(self):
        self.setProblem('debt')
        self.setAboutYouAnswers(on_benefits=YES)
        self.setBenefits(passported=True)
        response = self.client.get('/review')
        self.assertReviewSection('/about', response.data)

    def test_default_values_not_shown(self):
        self.setProblem('debt')
        self.setAboutYouAnswers(on_benefits=YES)
        self.setBenefits(passported=False)
        self.setBenefitsTaxCreditsAnswers(other_benefits=NO)
        response = self.client.get('/review')
        self.assertQuestionNotShown('total_other_benefit', response.data)
