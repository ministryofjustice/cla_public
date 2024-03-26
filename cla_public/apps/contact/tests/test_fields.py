from unittest import TestCase
from flask import current_app
from mock import patch
from cla_public.apps.contact.fields import time_slots_for_day
import datetime


class TestFeatureFlag(TestCase):
    @patch("cla_public.apps.contact.api.get_valid_callback_timeslots_on_date")
    @patch("cla_common.call_centre_availability.OpeningHours.time_slots")
    @patch("cla_public.apps.contact.fields.time_slots_for_day")
    def test_feature_flag_enabled(self, cla_backend_slots, cla_common_slots, get_timeslots):
        current_app.config["USE_BACKEND_CALLBACK_SLOTS"] = True
        date = datetime.date(2024, 1, 1)
        get_timeslots(date)
        cla_backend_slots.assert_called()
        cla_common_slots.assert_not_called()

    @patch("cla_public.apps.contact.api.get_valid_callback_timeslots_on_date")
    @patch("cla_common.call_centre_availability.OpeningHours.time_slots")
    @patch("cla_public.apps.contact.fields.time_slots_for_day")
    def test_feature_flag_disabled(self, cla_backend_slots, cla_common_slots, get_timeslots):
        current_app.config["USE_BACKEND_CALLBACK_SLOTS"] = False
        date = datetime.date(2024, 1, 1)
        get_timeslots(date)
        cla_backend_slots.assert_not_called()
        cla_common_slots.assert_called()
