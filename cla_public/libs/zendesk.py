# -*- coding: utf-8 -*-
"Zendesk"

import json
import requests
from flask import current_app


TICKETS_URL = 'https://ministryofjustice.zendesk.com/api/v2/tickets.json'


def create_ticket(payload):
    "Create a new Zendesk ticket"
    return requests.post(
        TICKETS_URL,
        data=json.dumps(payload),
        auth=(
            '{username}/token'.format(
                username=current_app.config['ZENDESK_API_USERNAME']),
            current_app.config['ZENDESK_API_TOKEN']
        ),
        headers={'content-type': 'application/json'})
