# -*- codeing: utf-8 -*-
"AddressFinder proxy api"

import requests
import urllib

from flask import current_app


def lookup(path, **kwargs):
    response = requests.get(
        '{host}/{path}?{params}'.format(
            host=current_app.config['ADDRESSFINDER_API_HOST'],
            path=path,
            params=urllib.urlencode(kwargs)),
        headers={
            'Authorization': 'Token {token}'.format(
                token=current_app.config['ADDRESSFINDER_API_TOKEN'])
        },
        timeout=current_app.config.get('API_CLIENT_TIMEOUT', None)
    )
    return response.text


def lookup_postcode(postcode, **kwargs):
    return lookup('/addresses/', **dict(
        kwargs,
        postcode=postcode))
