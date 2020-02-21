import json

import mock
from cla_public.apps.geocoder.views import geocode
from cla_public.apps.base.tests import FlaskAppTestCase


class GeocoderTest(FlaskAppTestCase):
    prerecorded_result = "Ministry of Justice\n52 Queen Annes Gate\nLondon\nSW1H 9AG"

    def setUp(self):
        super(GeocoderTest, self).setUp()
        self.app.config["OS_PLACES_API_KEY"] = "DUMMY_TOKEN"

    def test_response_packaging(self):
        expected_formatted_result = json.dumps([{"formatted_address": self.prerecorded_result}])

        with mock.patch("cla_common.address_lookup.ordnance_survey.FormattedAddressLookup.by_postcode") as mock_method:
            mock_method.return_value = [self.prerecorded_result]
            response = geocode(postcode="MOOT")
            self.assertEqual(expected_formatted_result, response.data)
