import json
import mock
import unittest

import postcodeinfo

from cla_public.app import create_app
from cla_public.apps.geocoder.views import geocode


class GeocoderTest(unittest.TestCase):

    def setUp(self):
        self.patch_client = mock.patch('postcodeinfo.Client')
        self.Client = self.patch_client.start()
        self.client = self.Client.return_value

        app = create_app('config/testing.py')
        app.config['TESTING'] = False
        app.config['POSTCODEINFO_API'] = {
                'api_url': 'test_url',
                'auth_token': 'DUMMY_TOKEN'}
        app.test_request_context().push()

    def tearDown(self):
        self.patch_client.stop()

    def test_lookup_addresses(self):
        postcode = 'sw1a1aa'
        address = 'Buckingham Palace\nLondon\nSW1A 1AA'
        addresses = [
            {'formatted_address': address}]

        self.client.lookup_postcode.return_value.addresses = addresses

        response = geocode(postcode)

        self.Client.assert_called_with(
            auth_token='DUMMY_TOKEN',
            api_url='test_url')

        self.client.lookup_postcode.assert_called_with(postcode)

        self.assertEqual(json.dumps(addresses), response.data)

    def test_server_error(self):

        def raise_exception(exception):

            def response(*args):
                raise exception

            return response

        cases = [
            postcodeinfo.NoResults,
            postcodeinfo.ServerException,
            postcodeinfo.ServiceUnavailable]

        for exception in cases:
            self.client.lookup_postcode.addresses.side_effect = \
                raise_exception(exception)

            response = geocode('sw1a1aa')

            self.assertEqual(json.dumps([]), response.data)
