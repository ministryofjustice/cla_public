# -*- coding: utf-8 -*-
"AddressFinder proxy views"

from flask import current_app, jsonify, request

from api import lookup
from cla_public.libs.api_proxy import on_timeout
from cla_public.apps.addressfinder_proxy import addressfinder, lookup
from cla_public.apps.addressfinder_proxy.mock import mock_addressfinder


@addressfinder.route('/addressfinder/<path:path>', methods=['GET'])
@on_timeout(response='[]')
def addressfinder_proxy_view(path):
    "Proxy addressfinder requests"

    if current_app.config.get('TESTING'):
        return mock_addressfinder(request.args)

    return lookup(path, **dict(request.args.items()))
