# -*- coding: utf-8 -*-

import requests
from flask import current_app


def check_backend_api():
    backend_healthcheck_url = '%s/%s' % (
        current_app.config['BACKEND_BASE_URI'], 'status/healthcheck.json')
    status = False
    response_content = None

    try:
        backend_healthcheck_response = requests.get(backend_healthcheck_url)
        status = True if backend_healthcheck_response.ok else backend_healthcheck_response.error
        response_content = backend_healthcheck_response.json()
    except requests.exceptions.RequestException as e:
        status = False
        response_content = e.__class__.__name__

    return {
        'status': status,
        'url': backend_healthcheck_url,
        'response': response_content
    }
