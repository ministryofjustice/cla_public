import logging

from cla_public.config.common import (
    GOVUK_NOTIFY_API_KEY,
    TESTING,
    DEBUG,
    EMAIL_ORCHESTRATOR_URL,
    USE_EMAIL_ORCHESTRATOR_FLAG,
)
from notifications_python_client.notifications import NotificationsAPIClient
from notifications_python_client.errors import HTTPError
import requests


log = logging.getLogger(__name__)


class GovUkNotify(object):
    def __new__(cls):
        """
        If this feature flag is set rather than creating a GovUkNotify object
        a NotifyEmailOrchestrator object will be created instead, overloading the send_email method.
        """
        if USE_EMAIL_ORCHESTRATOR_FLAG:
            return NotifyEmailOrchestrator()
        return super(GovUkNotify, cls).__new__(cls)

    def __init__(self):
        self.notifications_client = None
        if GOVUK_NOTIFY_API_KEY:
            self.notifications_client = NotificationsAPIClient(GOVUK_NOTIFY_API_KEY)
        elif not TESTING and not DEBUG:
            raise ValueError("Missing API Key for GOVUK Notify")

    def send_email(self, email_address, template_id, personalisation):
        if not self.notifications_client:
            log.info("No API key set, unable to send email")
            return
        try:
            self.notifications_client.send_email_notification(
                email_address=email_address,  # required string
                template_id=template_id,  # required UUID string
                personalisation=personalisation,
            )
        except HTTPError as error:
            log.error("GovUkNotify error: {}".format(str(error)))
            raise error


class NotifyEmailOrchestrator(object):
    def __init__(self):
        if not EMAIL_ORCHESTRATOR_URL:
            raise EnvironmentError("EMAIL_ORCHESTRATOR_URL is not set.")
        self.base_url = EMAIL_ORCHESTRATOR_URL
        self.endpoint = "email"

    def url(self):
        base_url = self.base_url if self.base_url.endswith("/") else self.base_url + "/"

        return base_url + self.endpoint

    def send_email(self, email_address, template_id, personalisation=None):
        data = {"email_address": email_address, "template_id": template_id}
        if personalisation:
            data["personalisation"] = personalisation

        response = requests.post(self.url(), json=data)

        if response.status_code != 201:
            raise HTTPError(response)
