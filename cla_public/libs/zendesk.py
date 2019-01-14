# coding: utf-8
"Zendesk"

import json
import requests
from flask import current_app


TICKETS_URL = "https://ministryofjustice.zendesk.com/api/v2/tickets.json"


def zendesk_auth():
    return (
        "{username}/token".format(username=current_app.config["ZENDESK_API_USERNAME"]),
        current_app.config["ZENDESK_API_TOKEN"],
    )


def create_ticket(payload):
    "Create a new Zendesk ticket"

    return requests.post(
        TICKETS_URL, data=json.dumps(payload), auth=zendesk_auth(), headers={"content-type": "application/json"}
    )


def tickets():
    "List Zendesk tickets"

    return requests.get(TICKETS_URL, auth=zendesk_auth())
