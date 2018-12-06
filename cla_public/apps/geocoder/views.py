# coding=utf-8
"""Geocoder proxy views"""

import json
import logging

from flask import Response, current_app

import requests

from cla_public.apps.geocoder import geocoder
from cla_public.apps.geocoder.mock_geocoder import mock_geocoder

log = logging.getLogger(__name__)


def format_address_from_result(raw_result):
    dpa_result = raw_result.get('DPA')
    if dpa_result:
        return format_address_from_dpa_result(dpa_result)
    # lpi_result = raw_result.get('LPI')
    # if lpi_result:
    #     return format_address_from_lpi_result(lpi_result)


def format_address_from_dpa_result(raw_result):
    formatted_components = []
    # TODO Merge lines for "BUILDING_NUMBER" and "THOROUGHFARE_NAME"
    for key in ["BUILDING_NAME", "BUILDING_NUMBER", "THOROUGHFARE_NAME", "DEPENDENT_LOCALITY", "POST_TOWN"]:
        formatted_components.append(raw_result.get(key, '').title())
    formatted_components.append(raw_result.get("POSTCODE", '').upper())
    return '\n'.join([c for c in formatted_components if c])


# def format_address_from_lpi_result(raw_result):
#     formatted_components = []
#     for key in ["PAO_START_NUMBER", "STREET_DESCRIPTION", "TOWN_NAME", "LOCAL_CUSTODIAN_CODE_DESCRIPTION"]:
#         formatted_components.append(raw_result.get(key, '').title())
#     formatted_components.append(raw_result.get("POSTCODE_LOCATOR", '').upper())
#     return '\n'.join([c for c in formatted_components if c])


@geocoder.route('/addresses/<postcode>', methods=['GET'])
def geocode(postcode):
    """Lookup addresses with the specified postcode"""

    if current_app.config.get('TESTING'):
        return mock_geocoder(postcode)

    response = []
    url = current_app.config.get('OS_PLACES_API_URL')
    key = current_app.config.get('OS_PLACES_API_KEY')
    params = {'postcode': postcode,
              'key': key,
              'output_srs': 'WGS84',
              'dataset': 'DPA',
              # 'maxresults': 100,  # TODO Consider postcodeinfo default maxresults
              # 'dataset': 'DPA,LPI'  # Only request DPA results by default. TODO Confirm exclusion of LPI results.
              #  See https://apidocs.os.uk/docs/os-places-lpi-output
              }
    try:
        os_places_response = requests.get(url, params, timeout=3)  # TODO lookup SLA, adjust timeout
        os_places_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        log.error('Requests error: {}'.format(e))
    else:
        try:
            os_places_results = os_places_response.json().get('results', {})
        except ValueError as e:
            log.warning('os_places_response JSON parse error: {}'.format(e))
        else:
            formatted_addresses = [format_address_from_result(result) for result in os_places_results]
            response = [{'formatted_address': address} for address in formatted_addresses if address]
    return Response(json.dumps(response), mimetype='application/json')
