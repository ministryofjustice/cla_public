import json
import unittest

import requests_mock

from cla_public.app import create_app
from cla_public.apps.geocoder.views import geocode


class GeocoderTest(unittest.TestCase):
    prerecorded_api_response = {'results': [{u'DPA': {u'ENTRY_DATE': u'20/06/2012',
                                                      u'POSTAL_ADDRESS_CODE_DESCRIPTION': u'A record which is linked to PAF',
                                                      u'LOCAL_CUSTODIAN_CODE_DESCRIPTION': u'CITY OF WESTMINSTER',
                                                      u'LOCAL_CUSTODIAN_CODE': 5990,
                                                      u'POSTCODE': u'SW1H 9AG',
                                                      u'UPRN': u'10033617916',
                                                      u'UDPRN': u'52712028',
                                                      u'ORGANISATION_NAME': u'MINISTRY OF JUSTICE',
                                                      u'POST_TOWN': u'LONDON',
                                                      u'LANGUAGE': u'EN',
                                                      u'CLASSIFICATION_CODE_DESCRIPTION': u'Office',
                                                      u'THOROUGHFARE_NAME': u'QUEEN ANNES GATE',
                                                      u'Y_COORDINATE': 179549.0,
                                                      u'BUILDING_NUMBER': u'52',
                                                      u'RPC': u'1',
                                                      u'LAST_UPDATE_DATE': u'10/02/2016',
                                                      u'LOGICAL_STATUS_CODE': u'1',
                                                      u'BLPU_STATE_CODE_DESCRIPTION': u'In use',
                                                      u'LNG': -0.1346249,
                                                      u'MATCH_DESCRIPTION': u'EXACT',
                                                      u'STATUS': u'APPROVED',
                                                      u'TOPOGRAPHY_LAYER_TOID': u'osgb1000001796535716',
                                                      u'BLPU_STATE_DATE': u'20/06/2012',
                                                      u'X_COORDINATE': 529576.0,
                                                      u'MATCH': 1.0,
                                                      u'POSTAL_ADDRESS_CODE': u'D',
                                                      u'ADDRESS': u'MINISTRY OF JUSTICE '
                                                                  u'52'
                                                                  u'QUEEN ANNES GATE'
                                                                  u'LONDON'
                                                                  u'SW1H 9AG',
                                                      u'LAT': 51.5000351,
                                                      u'BLPU_STATE_CODE': u'2'
                                                      }
                                             }]
                                }

    def setUp(self):
        app = create_app('config/testing.py')
        app.config['OS_PLACES_API_KEY'] = 'DUMMY_TOKEN'
        app.test_request_context().push()

    def test_response_formatting(self):
        postcode = 'SW1H9AG'
        expected_formatted_result = json.dumps([{'formatted_address': u'52\nQueen Annes Gate\nLondon\nSW1H 9AG'}])

        with requests_mock.Mocker() as m:
            m.get("https://api.ordnancesurvey.co.uk/places/v1/addresses/postcode", json=self.prerecorded_api_response)
            response = geocode(postcode)
            self.assertEqual(response.data, expected_formatted_result)
