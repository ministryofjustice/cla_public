# -*- coding: utf-8 -*-
"""CLA Public base decorators"""

import functools
from flask import jsonify
import requests

from cla_public.apps.base.constants import TIMEOUT_RETURN_ERROR


def api_proxy(return_value=TIMEOUT_RETURN_ERROR, json_response=False):
    def view(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout):
                if json_response:
                    return jsonify(return_value)
                return return_value

        return wrapper

    return view

