from unittest import TestCase
from flask import current_app
from mock import patch, Mock
from cla_public.apps.contact.fields import (
    AvailabilityCheckerForm,
    ThirdPartyAvailabilityCheckerForm,
    time_slots_for_day,
)
import datetime


class TestFeatureFlag(TestCase):
    @patch("cla_public.apps.contact.fields.get_valid_callback_timeslots_on_date")
    @patch("cla_public.apps.contact.fields.OpeningHours.time_slots")
    def test_feature_flag_enabled(self, cla_backend_slots, cla_common_slots):
        current_app.config["USE_BACKEND_CALLBACK_SLOTS"] = True
        date = datetime.date(2024, 1, 1)
        time_slots_for_day(date)
        cla_backend_slots.assert_called()
        cla_common_slots.assert_not_called()

    @patch("cla_public.apps.contact.fields.get_valid_callback_timeslots_on_date")
    @patch("cla_public.apps.contact.fields.OpeningHours.time_slots")
    def test_feature_flag_disabled(self, cla_backend_slots, cla_common_slots):
        current_app.config["USE_BACKEND_CALLBACK_SLOTS"] = False
        date = datetime.date(2024, 1, 1)
        time_slots_for_day(date)
        cla_backend_slots.assert_not_called()
        cla_common_slots.assert_called()


class TestCallbackForm(TestCase):
    @patch("cla_public.apps.contact.api.get_valid_callback_slots", Mock(return_value=[]))
    def test_field_attribute_set(self):
        form = AvailabilityCheckerForm()
        assert form.time_in_day.is_third_party_callback is False
        assert form.time_today.is_third_party_callback is False

    @patch("cla_public.apps.contact.fields.get_valid_callback_timeslots_on_date")
    @patch.dict(current_app.config, {"USE_BACKEND_CALLBACK_SLOTS": True})
    @patch("cla_public.apps.contact.api.get_valid_callback_slots", Mock(return_value=[]))
    def test_time_field_choices(self, get_timeslots):
        AvailabilityCheckerForm()
        get_timeslots.assert_called_with(datetime.date.today(), is_third_party_callback=False)

    @patch("cla_public.apps.contact.fields.time_slots_for_day")
    @patch.dict(current_app.config, {"USE_BACKEND_CALLBACK_SLOTS": True})
    @patch("cla_public.apps.contact.api.get_valid_callback_slots", Mock(return_value=[]))
    def test_time_field_day_change(self, get_timeslots):
        new_date = datetime.date(2024, 1, 1)
        form = AvailabilityCheckerForm()
        form.time_in_day.set_day_choices(new_date)
        get_timeslots.assert_called_with(new_date, False)

    @patch("cla_public.apps.contact.fields.get_valid_callback_days")
    @patch.dict(current_app.config, {"USE_BACKEND_CALLBACK_SLOTS": True})
    @patch("cla_public.apps.contact.api.get_valid_callback_slots", Mock(return_value=[]))
    def test_day_field_choices(self, get_valid_callback_days):
        AvailabilityCheckerForm()
        get_valid_callback_days.assert_called_with(include_today=False, is_third_party_callback=False)


class TestThirdPartyForm(TestCase):
    @patch("cla_public.apps.contact.api.get_valid_callback_slots", Mock(return_value=[]))
    def test_field_attribute_set(self):
        form = ThirdPartyAvailabilityCheckerForm()
        assert form.time_in_day.is_third_party_callback is True
        assert form.time_today.is_third_party_callback is True

    @patch("cla_public.apps.contact.fields.get_valid_callback_timeslots_on_date")
    @patch.dict(current_app.config, {"USE_BACKEND_CALLBACK_SLOTS": True})
    @patch("cla_public.apps.contact.api.get_valid_callback_slots", Mock(return_value=[]))
    def test_time_field_choices(self, get_timeslots):
        ThirdPartyAvailabilityCheckerForm()
        get_timeslots.assert_called_with(datetime.date.today(), is_third_party_callback=True)

    @patch("cla_public.apps.contact.fields.time_slots_for_day")
    @patch.dict(current_app.config, {"USE_BACKEND_CALLBACK_SLOTS": True})
    @patch("cla_public.apps.contact.api.get_valid_callback_slots", Mock(return_value=[]))
    def test_time_field_day_change(self, get_timeslots):
        new_date = datetime.date(2024, 1, 1)
        form = ThirdPartyAvailabilityCheckerForm()
        form.time_in_day.set_day_choices(new_date)
        get_timeslots.assert_called_with(new_date, True)

    @patch("cla_public.apps.contact.fields.get_valid_callback_days")
    @patch.dict(current_app.config, {"USE_BACKEND_CALLBACK_SLOTS": True})
    @patch("cla_public.apps.contact.api.get_valid_callback_slots", Mock(return_value=[]))
    def test_day_field_choices(self, get_valid_callback_days):
        ThirdPartyAvailabilityCheckerForm()
        get_valid_callback_days.assert_called_with(include_today=False, is_third_party_callback=True)
