# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import urllib2
from flask import url_for, session

from mock import Mock, patch
import re
import requests
import unittest
import urlparse
from werkzeug.datastructures import MultiDict
import xlrd

from cla_public import app
from cla_public.apps.checker.constants import NO, YES
from cla_public.apps.checker.forms import ProblemForm, AboutYouForm, \
    YourBenefitsForm, PropertiesForm, SavingsForm, TaxCreditsForm, \
    IncomeForm, OutgoingsForm, PropertyForm
from cla_public.apps.checker.tests.utils.forms_utils import \
    ProblemFormMixin, NON_FORM_FIELDS, \
    CATEGORY_MAPPING, AboutYouFormMixin, BenefitsFormMixin, \
    PropertiesFormMixin, SavingsFormMixin, TaxCreditsFormMixin, \
    IncomeFormMixin, OutgoingsFormMixin


FILE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'means_test.xlsx')

FORMS = {
    '/problem': ProblemForm,
    '/about': AboutYouForm,
    '/benefits': YourBenefitsForm,
    '/property': PropertiesForm,
    '/savings': SavingsForm,
    '/benefits-tax-credits': TaxCreditsForm,
    '/income': IncomeForm,
    '/outgoings': OutgoingsForm,
}

END_PAGES = {
    'P': '/result/eligible',
    'F': '/help-organisations/'
}


class MeansTestEntry(
    ProblemFormMixin,
    AboutYouFormMixin,
    BenefitsFormMixin,
    PropertiesFormMixin,
    SavingsFormMixin,
    TaxCreditsFormMixin,
    IncomeFormMixin,
    OutgoingsFormMixin,
):
    """Process data row from means test row and return values for each form"""
    def __init__(self, **values):
        self.__dict__.update(values)

    def get_value(self, form_class, field):
        return getattr(self, '%s_%s' % (form_class.__name__.lower(), field))()

    def get_form_data(self, form_class):
        method_name = '%s_data' % form_class.__name__.lower()
        if hasattr(self, method_name):
            return getattr(self, method_name)()
        return {name: self.get_value(form_class, name)
                for name in form_class()._fields.iterkeys()
                if name not in NON_FORM_FIELDS}

    def yes_or_no(self, spreadsheet_value, extra_cond=True):
        return YES if spreadsheet_value == 'Y' and extra_cond else NO

    def n_to_yes_no(self, n):
        return YES if self.n_greater_than(n) else NO

    def n_greater_than(self, n, x=0):
        try:
            return True if float(n) > x else False
        except (ValueError):
            return False

    def number_if_yes(self, n, d):
        return int(n) if n and int(n) > 0 and d == YES else None

    def get_total_if_partner(self, your_value, partner_value):
        val = 0.00
        if your_value:
            val += float(your_value)
        if session.has_partner and partner_value:
            val += float(partner_value)
        return val


class TestApiPayloads(unittest.TestCase):

    def setUp(self):
        self.book = xlrd.open_workbook(FILE_PATH)
        self.means_test_list = []

        self.app = app.create_app('config/testing.py')

        # self.download_from_google()
        self.parse_book()

        self._ctx = self.app.test_request_context()
        self._ctx.push()

        self.errors = []

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
            print 'Could not download'
            pass

    def parse_book(self):
        sheet = self.book.sheet_by_index(0)

        # read header values into the list
        keys = [
            self.to_key(sheet.cell(1, col_index).value)
            for col_index in xrange(sheet.ncols)
        ]

        for row_index in xrange(2, sheet.nrows):
            # If there is a test number is a test
            if sheet.cell(row_index, 0).value:
                d = {'_%s' % keys[col_index]: sheet.cell(row_index, col_index).value
                     for col_index in xrange(sheet.ncols) if keys[col_index]}
                if d['_law_area'] and d['_law_area'] in CATEGORY_MAPPING \
                        and not d['_non_public_tests']:
                    d['line_number'] = row_index + 1
                    mt = MeansTestEntry(**d)
                    self.means_test_list.append(mt)

    def post_to_form(self, test_case, client):
        form_class = FORMS[self.current_location]
        form_class_name = form_class.__name__
        form_data = test_case.get_form_data(form_class)
        resp = client.post(self.current_location, data=form_data)
        self.assertEquals(
            resp.status_code, 302,
            msg='Form validation error for line %s on form %s' %
                (test_case.line_number, form_class_name))

        self.current_location = urlparse.urlparse(resp.location).path

    def test_means_test(self):
        for test_case in self.means_test_list:
            with self.app.test_client() as client:
                resp = client.get(url_for('base.get_started'))
                self.current_location = urlparse.urlparse(resp.location).path
                while self.current_location in FORMS:
                    self.post_to_form(test_case, client)

                if test_case._actual in END_PAGES:
                    expected_page = END_PAGES[test_case._actual]
                    if expected_page not in self.current_location:
                        self.errors.append(
                            'Line: %s, %s, expected: %s and got %s. RESULT: %s'
                            % (test_case.line_number, test_case._description,
                                expected_page, self.current_location,
                                session.get('is_eligible', '(not set)')))

        for e in self.errors:
            print e

        self.assertEqual(len(self.errors), 0)





