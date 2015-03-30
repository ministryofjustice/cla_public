import requests
import json
from flask import current_app


class LaaLaaError(Exception):
    pass


def find(postcode, page=1):
    try:
        response = requests.get(
            '{host}/legal-advisers/?postcode={postcode}&format=json&page={page}'
            .format(
                host=current_app.config['LAALAA_API_HOST'],
                postcode=postcode,
                page=page
            )
        )
        try:
            return json.loads(response.content)
        except ValueError:
            raise LaaLaaError
    except (requests.exceptions.ConnectionError,
            requests.exceptions.Timeout) as e:
        raise LaaLaaError(e)
