import json
import requests
from flask import current_app

TICKETS_URL = 'https://ministryofjustice.zendesk.com/api/v2/tickets.json'

class ZD(object):
    def post_to_zendesk(self, payload):
        headers = { 'content-type': 'application/json' }

        return requests.post(
            TICKETS_URL,
            data=json.dumps(payload),
            auth=(
                current_app.config['ZENDESK_API_USERNAME']+'/token',
                current_app.config['ZENDESK_API_TOKEN']
            ),
            headers=headers)
