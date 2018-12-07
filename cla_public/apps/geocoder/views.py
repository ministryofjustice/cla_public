# coding=utf-8
"""Geocoder proxy views"""

import json
import logging

from cla_common.address_lookup.ordnance_survey import OsAddressLookupFormatted
from flask import Response, current_app

from cla_public.apps.geocoder import geocoder
from cla_public.apps.geocoder.mock_geocoder import mock_geocoder

log = logging.getLogger(__name__)


@geocoder.route('/addresses/<postcode>', methods=['GET'])
def geocode(postcode):
    """Lookup addresses with the specified postcode"""

    if current_app.config.get('TESTING'):
        return mock_geocoder(postcode)

    key = current_app.config.get('OS_PLACES_API_KEY')
    formatted_addresses = OsAddressLookupFormatted(key=key).lookup_postcode(postcode)
    response = [{'formatted_address': address} for address in formatted_addresses if address]
    return Response(json.dumps(response), mimetype='application/json')
