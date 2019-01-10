# coding: utf-8
"""Decorator for API proxy views"""

import functools
import json
import logging
from requests.exceptions import ConnectTimeout, ReadTimeout


TIMEOUT_RESPONSE = json.dumps({"error": "Request timeout."})


log = logging.getLogger(__name__)


def on_timeout(response=TIMEOUT_RESPONSE):
    "Decorator for view functions which proxy API calls"

    def view(view_func):
        "Wrapped view function"

        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            "Wraps the view function with API timeout handling"

            try:
                return view_func(*args, **kwargs)
            except ConnectTimeout as conn_exception:
                log.exception("Connection timeout for API: %s", conn_exception)
            except ReadTimeout as read_exception:
                log.exception("Read timeout for API: %s", read_exception)
            return response

        return wrapper

    return view
