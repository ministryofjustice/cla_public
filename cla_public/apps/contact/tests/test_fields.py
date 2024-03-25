from unittest import TestCase
from flask import current_app
from mock import patch
from cla_public.apps.contact.fields import time_slots_for_day
import datetime


class TestFeatureFlag(TestCase):
    @patch("cla_public.apps.contact.api.get_valid_callback_timeslots_on_date")
    @patch("cla_common.call_centre_availability.OpeningHours.time_slots")
    def test_feature_flag_enabled(self, backend_timeslots, cla_common_timeslots):
        current_app.config["USE_BACKEND_CALLBACK_SLOTS"] = True
        date = datetime.date(2024, 1, 1)
        time_slots_for_day(date)
        backend_timeslots.assert_called()
        cla_common_timeslots.assert_not_called()

    @patch("cla_public.apps.contact.api.get_valid_callback_timeslots_on_date")
    @patch("cla_common.call_centre_availability.OpeningHours.time_slots")
    def test_feature_flag_disabled(self, backend_timeslots, cla_common_timeslots):
        current_app.config["USE_BACKEND_CALLBACK_SLOTS"] = False
        date = datetime.date(2024, 1, 1)
        time_slots_for_day(date)
        backend_timeslots.assert_not_called()
        cla_common_timeslots.assert_called()
