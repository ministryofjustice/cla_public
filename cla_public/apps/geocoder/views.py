# -*- coding: utf-8 -*-
"Geocoder proxy views"

import json

from flask import Response, current_app, request

import postcodeinfo

from cla_public.apps.geocoder import geocoder
from cla_public.apps.geocoder.mock_geocoder import mock_geocoder


@geocoder.route('/addresses/<postcode>', methods=['GET'])
def geocode(postcode):
    "Lookup addresses with the specified postcode"

    if current_app.config.get('TESTING'):
        return mock_geocoder(postcode)

    client = postcodeinfo.Client(**current_app.config.get('POSTCODEINFO_API'))
    postcode = client.lookup_postcode(postcode)

    try:
        response = [
            {'formatted_address': addr['formatted_address']}
            for addr in postcode.addresses]

    except postcodeinfo.PostcodeInfoException:
        response = []

    return Response(json.dumps(response), mimetype='application/json')
