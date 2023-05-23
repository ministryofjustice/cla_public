import logging

from cla_public.config.common import GOVUK_NOTIFY_API_KEY, TESTING, DEBUG
from notifications_python_client.notifications import NotificationsAPIClient
from notifications_python_client.errors import HTTPError


log = logging.getLogger(__name__)


class GovUkNotify(object):
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
