import os
import unittest
import urlparse

from bs4 import BeautifulSoup
from cla_common.address_lookup.ordnance_survey import AddressLookup
from flask import url_for, _request_ctx_stack

from cla_public import app
from cla_public.apps.checker import api
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

    def test_can_lookup_postcode(self):
        """Lookup a postcode with OS Places"""
        postcode_to_lookup = 'SW1A 1AA'
        os_places_key = self.app.config.get('OS_PLACES_API_KEY')
        addresses = AddressLookup(key=os_places_key).by_postcode(postcode_to_lookup)
        self.assertGreater(len(addresses), 0)
        result_postcode = addresses[0].get('DPA', {}).get('POSTCODE')
        self.assertEqual(result_postcode, postcode_to_lookup)

    def test_can_access_zendesk(self):
        "connect to Zendesk"
        with self.app.test_client():
            zendesk.tickets()

    def test_can_access_laalaa(self):
        "search for legal advisers on LAALAA"
        with self.app.test_client():
            laalaa.find('sw1a1aa')

    def test_can_access_sendgrid(self):
        "connect to SendGrid"
        with self.app.test_client():
            self.app.mail.connect()

    def test_can_access_backend(self):
        "connect to the backend"
        with self.app.test_client():
            api.get_api_connection()

    def test_can_use_scope_diagnosis(self):
        "use scope diagnosis"
        with self.app.test_client() as client:
            response = client.get(url_for('base.get_started'))
            url = urlparse.urlparse(response.location).path
            response = client.get(url)

            # Check the number of scope options
            scope_options_item = BeautifulSoup(response.data).find_all(
                class_='scope-options-list-item')
            self.assertEquals(len(scope_options_item), 16)

            # Follow the third option's link (Debt) and check the
            # there are options on the following screen
            response = client.get(scope_options_item[2].find('a').get('href'))
            scope_options_item = BeautifulSoup(response.data).find_all(
                class_='scope-options-list-item')
            self.assertTrue(len(scope_options_item) > 0)

            # Follow the first option's link (You own your own home)
            # and check the number of options on the following screen
            response = client.get(scope_options_item[0].find('a').get('href'))
            self.assertEquals(response.status_code, 302)
            self.assertTrue(
                str.find(response.data, '/legal-aid-available') > -1)
