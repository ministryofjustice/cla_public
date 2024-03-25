from unittest import TestCase
from flask import current_app
from mock import patch
from cla_public.apps.contact.forms import ContactForm
from cla_public.apps.checker.constants import CONTACT_PREFERENCE, CONTACT_PREFERENCE_NO_CALLBACK
import datetime


class TestContactFormChoices(TestCase):
    def test_valid_slots(self):
        pass

    @patch("cla_public.apps.contact.forms.ContactForm.update_contact_preference")
    def test_feature_flag_disabled(self, update_preference):
        current_app.config["USE_BACKEND_CALLBACK_SLOTS"] = False
        ContactForm()
        update_preference.assert_not_called()

    @patch("cla_public.apps.contact.forms.ContactForm.update_contact_preference")
    def test_feature_flag_enabled(self, update_preference):
        current_app.config["USE_BACKEND_CALLBACK_SLOTS"] = True
        ContactForm()
        update_preference.assert_called()

    @patch("cla_public.apps.contact.api.get_valid_callback_days", return_value=[])
    def test_no_slots_available(self, _):
        current_app.config["USE_BACKEND_CALLBACK_SLOTS"] = True
        form = ContactForm()
        form.contact_type.choices = CONTACT_PREFERENCE_NO_CALLBACK

    @patch("cla_public.apps.contact.api.get_valid_callback_days", return_value=[datetime.datetime(2024, 1, 1, 0, 0)])
    def test_slots_available(self, _):
        current_app.config["USE_BACKEND_CALLBACK_SLOTS"] = True
        form = ContactForm()
        form.contact_type.choices = CONTACT_PREFERENCE
