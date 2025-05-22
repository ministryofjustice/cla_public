from unittest import TestCase
from flask import current_app
from mock import patch
from cla_public.apps.checker.constants import CONTACT_PREFERENCE, CONTACT_PREFERENCE_NO_CALLBACK


class TestContactFormChoices(TestCase):
    def test_valid_slots(self):
        pass

    @patch("cla_public.apps.contact.forms.ContactForm.update_contact_preference")
    @patch("cla_public.apps.contact.forms.ContactForm")
    def test_feature_flag_disabled(self, update_preference, ContactForm):
        current_app.config["USE_BACKEND_CALLBACK_SLOTS"] = False
        ContactForm()
        update_preference.assert_not_called()

    @patch("cla_public.apps.contact.forms.ContactForm.update_contact_preference")
    @patch("cla_public.apps.contact.forms.ContactForm")
    def test_feature_flag_enabled(self, update_preference, ContactForm):
        current_app.config["USE_BACKEND_CALLBACK_SLOTS"] = True
        ContactForm()
        update_preference.assert_called()

    @patch("cla_public.apps.contact.forms.ContactForm")
    def test_no_slots_available(self, ContactForm):
        current_app.config["USE_BACKEND_CALLBACK_SLOTS"] = True
        form = ContactForm()
        form.contact_type.choices = CONTACT_PREFERENCE_NO_CALLBACK

    @patch("cla_public.apps.contact.forms.ContactForm")
    def test_slots_available(self, ContactForm):
        current_app.config["USE_BACKEND_CALLBACK_SLOTS"] = True
        form = ContactForm()
        form.contact_type.choices = CONTACT_PREFERENCE
