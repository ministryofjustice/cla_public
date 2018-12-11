# coding=utf-8
"""Geocoder proxy views"""

import json
import logging

from cla_common.address_lookup.ordnance_survey import FormattedAddressLookup
from flask import Response, current_app

from cla_public.apps.geocoder import geocoder

log = logging.getLogger(__name__)


@geocoder.route('/addresses/<postcode>', methods=['GET'])
def geocode(postcode):
    """Lookup addresses with the specified postcode"""
    key = current_app.config.get('OS_PLACES_API_KEY')
    formatted_addresses = FormattedAddressLookup(key=key).by_postcode(postcode)
    response = [{'formatted_address': address} for address in formatted_addresses if address]
    return Response(json.dumps(response), mimetype='application/json')
