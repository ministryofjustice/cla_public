import logging

from cla_public.config.common import TESTING, DEBUG, EMAIL_ORCHESTRATOR_URL
from notifications_python_client.errors import HTTPError
import requests


log = logging.getLogger(__name__)


class NotifyEmailOrchestrator(object):
    def __init__(self):
        self.base_url = None
        if EMAIL_ORCHESTRATOR_URL:
            self.base_url = EMAIL_ORCHESTRATOR_URL
        elif not TESTING and not DEBUG:
            raise EnvironmentError("EMAIL_ORCHESTRATOR_URL is not set.")
        self.endpoint = "email"

    def url(self):
        base_url = self.base_url if self.base_url.endswith("/") else self.base_url + "/"

        return base_url + self.endpoint

    def send_email(self, email_address, template_id, personalisation=None):
        if TESTING or DEBUG:
            log.info("Application is in TESTING mode, will not send email")
            return
        
        if not self.base_url:
            log.error("EMAIL_ORCHESTRATOR_URL is not set, unable to send email")

        data = {"email_address": email_address, "template_id": template_id}
        if personalisation:
            data["personalisation"] = personalisation

        response = requests.post(self.url(), json=data)

        if response.status_code != 201:
            raise HTTPError(response)
