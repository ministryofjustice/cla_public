# -*- coding: utf-8 -*-
from decimal import Decimal
import logging
import os
from pprint import pformat
import re
import unicodedata
import unittest
import urlparse

from bs4 import BeautifulSoup
from flask import session, url_for
import xlrd

from cla_public import app
from cla_public.apps.checker.forms import ProblemForm, AboutYouForm, \
    YourBenefitsForm, PropertiesForm, SavingsForm, TaxCreditsForm, \
    IncomeForm, OutgoingsForm, ReviewForm
from cla_public.apps.checker.means_test import MeansTest
from cla_public.apps.checker.tests.utils.forms_utils import CATEGORY_MAPPING, \
    FormDataConverter


logging.getLogger('MARKDOWN').setLevel(logging.WARNING)


SPREADSHEET_PATH = os.path.join(
    os.path.dirname(__file__),
    'data/means_test.xlsx')


class TestMeansTest(unittest.TestCase):

    def setUp(self):
        self.app = app.create_app('config/testing.py')
        ctx = self.app.test_request_context()
        ctx.push()
        self.client = self.app.test_client()

    def assertMeansTest(self, expected_result, case):
        with self.client as client:

            resp = client.get(url_for('base.get_started'))
            url = urlparse.urlparse(resp.location).path

            def error_msg(msg):
                mt = MeansTest()
                mt.update_from_session(session)
                return (
                    '{msg}\n'
                    'Means test: {data}\n').format(
                        msg=msg,
                        data=pformat(dict(mt)))

            form_class = get_form(url)
            while form_class:
                post_data = form_data(form_class, case)
                response = client.post(url, data=post_data)

                def form_errors():
                    return ' * ' + '\n * '.join([
                        error.text.strip() for error in
                        BeautifulSoup(response.data).select('.field-error')])

                self.assertRedirectToNextForm(response, error_msg((
                    'Validation error in {form}\n'
                    'Errors:\n{errors}\n'
                    'POST data:\n{data}').format(
                        form=form_class.__name__,
                        data=pformat(post_data),
                        errors=form_errors())))

                url = urlparse.urlparse(response.location).path
                form_class = get_form(url)

            result = 'unknown'

            if '/result/eligible' in url:
                result = 'eligible'

            if '/help-organisations/' in url:
                result = 'ineligible'

            self.assertEqual(expected_result, result, error_msg(
                'Expected {expected}, got {actual}'.format(
                    expected=expected_result,
                    actual=result)))

    def assertRedirectToNextForm(self, response, message):
        self.assertEquals(response.status_code, 302, message)


def form_data(form_class, case):
    """
    Convert spreadsheet case data to form data
    """
    return FormDataConverter(**case).get_form_data(form_class)


def get_form(url):
    return {
        '/problem': ProblemForm,
        '/about': AboutYouForm,
        '/benefits': YourBenefitsForm,
        '/property': PropertiesForm,
        '/savings': SavingsForm,
        '/benefits-tax-credits': TaxCreditsForm,
        '/income': IncomeForm,
        '/outgoings': OutgoingsForm,
        '/review': ReviewForm
    }.get(url)


def slugify(val):
    """
    Convert a string to something safe to use in a method name
    """
    slug = unicodedata.normalize('NFKD', unicode(val))
    slug = slug.encode('ascii', 'ignore').lower()
    slug = re.sub(r'[^a-z0-9]+', '_', slug).strip('_')
    slug = re.sub(r'__+', '_', slug)
    return slug


def value(cell):
    """
    Decode the cell value to a Decimal if numeric
    """
    if isinstance(cell.value, float):
        return Decimal(str(cell.value))
    return cell.value


def spreadsheet():
    """
    Generator for the rows of the spreadsheet
    """
    book = xlrd.open_workbook(SPREADSHEET_PATH)
    sheet = book.sheet_by_index(0)
    cols = ['_' + slugify(sheet.cell(1, i).value) for i in xrange(sheet.ncols)]
    cols.append('line_number')
    for row in xrange(2, sheet.nrows):
        cells = [value(sheet.cell(row, i)) for i in xrange(sheet.ncols)]
        cells.append(row + 1)
        yield dict(zip(cols, cells))


def is_test(row):
    """
    True if the row represents a test case
    """
    law_area = row.get('_law_area')
    non_public = row.get('_non_public_tests')
    return law_area in CATEGORY_MAPPING and not non_public
is_test.__test__ = False


def test_name(row):
    """
    Generate the method name for the test
    """
    return 'test_{0}_{1}'.format(
        row.get('line_number'),
        slugify(row.get('_description')))
test_name.__test__ = False


def make_test(row):
    """
    Generate a test method
    """
    def row_test(self):
        actual = row.get('_actual')
        if actual in ('P', 'F'):
            if actual == 'P':
                self.assertMeansTest('eligible', row)
            else:
                self.assertMeansTest('ineligible', row)
    row_test.__doc__ = str(row.get('line_number')) + ': ' + row.get('_description')
    return row_test
make_test.__test__ = False


def create_tests():
    """
    Insert test methods into the TestCase for each case in the spreadsheet
    """
    for row in spreadsheet():
        if is_test(row):
            setattr(TestMeansTest, test_name(row), make_test(row))
create_tests.__test__ = False

create_tests()
