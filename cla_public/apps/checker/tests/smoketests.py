import os
import unittest
import urlparse

from bs4 import BeautifulSoup
from flask import url_for, _request_ctx_stack

from cla_public import app
from cla_public.apps import addressfinder_proxy
from cla_public.apps.checker import api
from cla_public.apps.checker.tests import test_integration as util
from cla_public.libs import laalaa, zendesk


class SmokeTests(unittest.TestCase):

    def setUp(self):
        config_file = 'config/docker.py'
        if os.environ.get('CLA_ENV') is None:
            config_file = 'config/common.py'
        self.app = app.create_app(config_file)
        self.app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
        self.ctx = self.app.test_request_context()
        self.ctx.push()

    def tearDown(self):
        if _request_ctx_stack.top and _request_ctx_stack.top.preserved:
            _request_ctx_stack.top.pop()
        self.ctx.pop()
        self.ctx = None

    def test_can_access_addressfinder(self):
        "lookup a postcode with AddressFinder"
        with self.app.test_client() as client:
            addressfinder_proxy.lookup_postcode('sw1a1aa')

    def test_can_access_zendesk(self):
        "connect to Zendesk"
        with self.app.test_client() as client:
            zendesk.tickets()

    def test_can_access_laalaa(self):
        "search for legal advisers on LAALAA"
        with self.app.test_client() as client:
            laalaa.find('sw1a1aa')

    def test_can_access_backend(self):
        "connect to the backend"
        with self.app.test_client() as client:
            conn = api.get_api_connection()

    def test_can_set_category(self):
        "submit the problem form"
        with self.app.test_client() as client:
            response = client.get(url_for('base.get_started'))
            url = urlparse.urlparse(response.location).path
            form_class = util.get_form(url)
            response = client.get(url)
            csrf_token = BeautifulSoup(response.data).find(id='csrf_token')['value']

            post_data = util.form_data(form_class, {'_law_area': 'Debt'})
            post_data['csrf_token'] = csrf_token
            response = client.post(url, data=post_data)
            self.assertEquals(response.status_code, 302)
