from notifications_python_client.notifications import NotificationsAPIClient
from cla_public.config.common import GOVUK_NOTIFY_API_KEY


class GovUkNotify(object):
    def __init__(self):
        if GOVUK_NOTIFY_API_KEY:
            self.notifications_client = NotificationsAPIClient(GOVUK_NOTIFY_API_KEY)
        else:
            raise ValueError("Missing API Key for GOVUK Notify")

    def send_email(self, email_address, template_id, personalisation):
        self.notifications_client.send_email_notification(
            email_address=email_address,  # required string
            template_id=template_id,  # required UUID string
            personalisation=personalisation,
        )
