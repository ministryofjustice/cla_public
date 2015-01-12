# -*- coding: utf-8 -*-
"AddressFinder proxy views"

import requests
import urllib

from flask import current_app, jsonify, request

from cla_public.libs.api_proxy import on_timeout
from cla_public.apps.addressfinder_proxy import addressfinder
from cla_public.apps.addressfinder_proxy.mock import mock_addressfinder


@addressfinder.route('/addressfinder/<path:path>', methods=['GET'])
@on_timeout(response='[]')
def addressfinder_proxy_view(path):
    "Proxy addressfinder requests"

    if current_app.config.get('TESTING'):
        return mock_addressfinder(request.args)

    response = requests.get(
        '{host}/{path}?{params}'.format(
            host=current_app.config['ADDRESSFINDER_API_HOST'],
            path=path,
            params=urllib.urlencode(request.args)),
        headers={
            'Authorization': 'Token {token}'.format(
                token=current_app.config['ADDRESSFINDER_API_TOKEN'])
        },
        timeout=current_app.config.get('API_CLIENT_TIMEOUT', None)
    )
    return response.text
