# -*- coding: utf-8 -*-
import os
import urllib2
from flask import url_for, session

from mock import Mock, patch
import re
import requests
import unittest
import urlparse
import xlrd

from cla_public import app
from cla_public.apps.checker.forms import ProblemForm, AboutYouForm, \
    YourBenefitsForm, PropertiesForm, SavingsForm, TaxCreditsForm, \
    IncomeForm, OutgoingsForm


FILE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'means_test.xlsx')


FORMS = {
    '/problem': ProblemForm,
    # '/about': AboutYouForm,
    # '/benefits': YourBenefitsForm,
    # '/property': PropertiesForm,
    # '/savings': SavingsForm,
    # '/benefits-tax-credits': TaxCreditsForm,
    # '/income': IncomeForm,
    # '/outgoings': OutgoingsForm,
}


CATEGORY_MAPPING = {
    'Welfare': 'benefits',
    'Debt': 'debt',
}


class MeansTestEntry(object):
    """Process data row from means test row and return values for each form"""
    def __init__(self, **values):
        self.__dict__.update(values)

    @property
    def problemform_categories(self):
        return CATEGORY_MAPPING[self.law_area]

    @property
    def problemform_data(self):
        return {
            'categories': self.problemform_categories
        }


class TestApiPayloads(unittest.TestCase):

    def setUp(self):
        self.book = xlrd.open_workbook(FILE_PATH)
        self.means_test_list = []

        self.app = app.create_app('config/testing.py')

        # self.download_from_google()
        self.parse_book()

        self._ctx = self.app.test_request_context()
        self._ctx.push()

    def tearDown(self):
        pass

    def to_key(self, key):
        return unicode(key).lower().replace(' ', '_')

    def download_from_google(self):
        try:
            spreadsheet_id = '1idIleO4-mNTM0pW6-aOcMwXgK_0yjrpL7YkHHeuWL5c'
            response = requests.get(
                'https://docs.google.com/spreadsheets/d/%s/export?format=xlsx'
                % spreadsheet_id)
            assert response.status_code == 200, 'Wrong status code'
            s = file(FILE_PATH, 'w')
            s.write(response.content)
            s.close()
        except AssertionError:
            pass

    def parse_book(self):
        sheet = self.book.sheet_by_index(0)

        # read header values into the list
        keys = [
            self.to_key(sheet.cell(1, col_index).value)
            for col_index in xrange(sheet.ncols)
        ]

        for row_index in xrange(2, sheet.nrows):
            # If there is a test number - so is a teszt
            if sheet.cell(row_index, 0).value:
                d = {keys[col_index]: sheet.cell(row_index, col_index).value
                     for col_index in xrange(sheet.ncols) if keys[col_index]}
                if d['law_area'] and d['law_area'] in CATEGORY_MAPPING:
                    d['line_number'] = row_index + 1
                    mt = MeansTestEntry(**d)
                    self.means_test_list.append(mt)

    def post_to_form(self, test_case, client):
        form_class = FORMS[self.current_location]
        form = form_class()
        form_data = getattr(test_case, '%s_data' % form_class.__name__.lower())
        resp = client.post(self.current_location, data=form_data)
        self.assertEquals(
            resp.status_code, 302,
            msg='Form validation error for line %s on form %s' %
                (test_case.line_number, form_class.__name__))

        for field_name, field in form._fields.iteritems():
            if field_name not in ['csrf_token', 'comment']:
                self.assertEquals(
                    session.get('%s_%s' % (form_class.__name__, field_name)),
                    test_case.problemform_categories,
                    msg='Field not in session for line %s on form %s and '
                        'field %s: %s != %s' % (
                        test_case.line_number,
                        form_class.__name__,
                        field_name,
                        session.get('%s_%s' % (form_class.__name__, field_name)),
                        test_case.problemform_categories))
            self.current_location = urlparse.urlparse(resp.location).path

    def test_means_test(self):
        for test_case in self.means_test_list:
            with self.app.test_client() as client:
                resp = client.get(url_for('base.get_started'))
                self.current_location = urlparse.urlparse(resp.location).path
                while self.current_location in FORMS:
                    self.post_to_form(test_case, client)

        self.assertTrue(True)





