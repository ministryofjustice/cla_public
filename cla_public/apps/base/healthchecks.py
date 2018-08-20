# -*- coding: utf-8 -*-

import os
import requests
from flask import current_app


def check_disk():
    stat = os.statvfs(os.getcwd())
    available_mb = (stat.f_bavail * stat.f_frsize) / (1024.0 ** 2)
    total_mb = (stat.f_blocks * stat.f_frsize) / (1024.0 ** 2)

    available_percent = available_mb / total_mb * 100
    status = True if available_percent > 2.0 else False

    return {
        'status': status,
        'available_percent': available_percent,
        'available_mb': available_mb,
        'total_mb': total_mb,
    }


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
