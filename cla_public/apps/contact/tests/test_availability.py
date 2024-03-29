from contextlib import contextmanager
import datetime
import logging
from mock import Mock
import unittest
import mock

from wtforms import Form
from wtforms.validators import InputRequired, ValidationError

from cla_common import call_centre_availability
from cla_public.apps.contact.constants import DAY_TODAY, DAY_SPECIFIC
from cla_public.apps.contact.fields import AvailableSlot, DayChoiceField, OPERATOR_HOURS, TimeChoiceField
from cla_public.apps.contact.forms import ContactForm, CallBackForm
from cla_public.apps.base.tests import FlaskAppTestCase
from werkzeug.datastructures import ImmutableMultiDict


logging.getLogger("MARKDOWN").setLevel(logging.WARNING)


@contextmanager
def override_current_time(dt):
    def override():
        return dt

    original = call_centre_availability.current_datetime
    call_centre_availability.current_datetime = override
    yield
    call_centre_availability.current_datetime = original


def bank_holidays():
    return [datetime.datetime(2014, 12, 25, 0, 0), datetime.datetime(2015, 5, 25, 0, 0)]


class TestAvailability(FlaskAppTestCase):
    def setUp(self):
        super(TestAvailability, self).setUp()
        self.now = datetime.datetime(2014, 11, 24, 9, 30)
        self.validator = None
        self.patcher = mock.patch("cla_common.call_centre_availability.bank_holidays", bank_holidays)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        super(TestAvailability, self).tearDown()

    def assertTimeValidationError(self):
        mock_form = Mock()
        mock_field = Mock()
        mock_field.data = None
        with self.assertRaises(ValidationError) as context:
            self.validator(mock_form, mock_field)
            self.assertTrue("Not a valid time" in str(context.exception))

    def assertAvailable(self, time, form=None):
        form = form or Mock()
        field = Mock()
        field.data = time
        with override_current_time(self.now):
            try:
                self.validator(form, field)

            except ValidationError as e:
                self.fail("{time} was not available at {now}: {exc}".format(time=time, now=self.now, exc=e))

    def assertNotAvailable(self, time, form=None):
        form = form or Mock()
        field = Mock()
        field.data = time
        with override_current_time(self.now):
            try:
                self.validator(form, field)
            except ValidationError:
                pass
            else:
                self.fail("{time} was available at {now}".format(time=time, now=self.now))

    def test_no_time_selected(self):
        # check that this raises a validation error
        self.validator = AvailableSlot(DAY_TODAY)
        self.assertTimeValidationError()
        self.validator = AvailableSlot(DAY_SPECIFIC)
        self.assertTimeValidationError()

    def test_available_slot_today_next_slot(self):

        self.validator = AvailableSlot(DAY_TODAY)
        self.assertNotAvailable(datetime.time(11, 0))
        self.assertAvailable(datetime.time(11, 30))

    def test_available_slot_today_before_9am(self):
        self.validator = AvailableSlot(DAY_TODAY)
        self.assertNotAvailable(datetime.time(8, 0))

    def test_available_slot_today_after_8pm(self):
        self.validator = AvailableSlot(DAY_TODAY)
        self.assertNotAvailable(datetime.time(20, 0))

    def test_available_slot_specific_day(self):
        self.validator = AvailableSlot(DAY_SPECIFIC)
        form = Mock()
        form.day.data = datetime.date(2014, 11, 25)
        self.assertAvailable(datetime.time(9, 0), form=form)

        form.day.data = datetime.date(2014, 11, 24)
        self.assertNotAvailable(datetime.time(9, 0), form=form)

        form.day.data = datetime.date(2014, 11, 30)
        self.assertNotAvailable(datetime.time(9, 0), form=form)

    def assertMondayMorningAvailable(self, form):
        self.assertAvailable(datetime.time(9, 0), form=form)
        self.assertAvailable(datetime.time(9, 30), form=form)
        self.assertAvailable(datetime.time(10, 0), form=form)
        self.assertAvailable(datetime.time(10, 30), form=form)

    def test_monday_9to11_available_after_eod_friday(self):
        """
        After removing Monday morning callback capping:
        Test Monday morning callbacks can be booked after hours on Friday, and on Saturday and Sunday.
        Test Tuesday morning callbacks, following a bank holiday Monday, can be booked 0900 - 1100.
        """
        times = {
            "after_hours_friday": datetime.datetime(2015, 2, 6, 20, 1),
            "saturday": datetime.datetime(2015, 2, 7, 9, 0),
            "sunday": datetime.datetime(2015, 2, 8, 9, 0),
        }
        monday = datetime.date(2015, 2, 9)
        for time in times.values():
            self.now = time
            self.validator = AvailableSlot(DAY_SPECIFIC)
            form = Mock()
            form.day.data = monday
            self.assertMondayMorningAvailable(form)

        # Tuesday after bank holiday
        with override_current_time(datetime.datetime(2015, 5, 24, 9, 30)):
            tuesday = datetime.date(2015, 5, 26)
            for time in times.values():
                self.now = time
                self.validator = AvailableSlot(DAY_SPECIFIC)
                form = Mock()
                form.day.data = tuesday
                self.assertMondayMorningAvailable(form)

    def test_bank_holiday_monday_before_11(self):
        """
        After removing Monday morning callback capping:
        Test callbacks can be booked all usual working hours on Tuesday following a bank holiday.
        """
        with override_current_time(datetime.datetime(2015, 5, 23, 10, 30)):
            tuesday_after_bank_holiday = datetime.datetime(2015, 5, 26, 9, 30)
            self.assertTrue(OPERATOR_HOURS.can_schedule_callback(tuesday_after_bank_holiday))

            tuesday_after_bank_holiday_after_11 = datetime.datetime(2015, 5, 26, 11, 30)
            self.assertTrue(OPERATOR_HOURS.can_schedule_callback(tuesday_after_bank_holiday_after_11))

            wed_after_bank_holiday = datetime.datetime(2015, 5, 27, 9, 30)
            self.assertTrue(OPERATOR_HOURS.can_schedule_callback(wed_after_bank_holiday))

    def test_booking_on_actual_bank_holiday(self):
        with override_current_time(datetime.datetime(2015, 5, 25, 10, 30)):
            tuesday = datetime.datetime(2015, 5, 26, 9, 30)
            self.assertTrue(OPERATOR_HOURS.can_schedule_callback(tuesday))

            tuesday_after_11 = datetime.datetime(2015, 5, 26, 11, 30)

            self.assertTrue(OPERATOR_HOURS.can_schedule_callback(tuesday_after_11))

    def test_booking_on_non_bank_holiday(self):
        with override_current_time(datetime.datetime(2015, 5, 9, 10, 30)):
            monday = datetime.datetime(2015, 5, 11, 9, 30)
            self.assertTrue(OPERATOR_HOURS.can_schedule_callback(monday))

            monday_after_11 = datetime.datetime(2015, 5, 11, 11, 30)

            self.assertTrue(OPERATOR_HOURS.can_schedule_callback(monday_after_11))


class TestDayTimeChoices(unittest.TestCase):
    def assertDayInChoices(self, day, choices):
        self.assertIn(day, [d for d, _ in choices])

    def test_day_time_choices(self):
        with override_current_time(datetime.datetime(2015, 2, 13, 21)):
            form = Mock()
            field = DayChoiceField()
            field = field.bind(form, "day")
            choices = field.day_time_choices
            # lower availability on saturday
            self.assertEqual(7, len(choices["20150214"]))
            # can book before 11am on monday. Monday morning call back capping removed.
            self.assertEqual(22, len(choices["20150216"]))
            # can book any slot on tuesday
            self.assertEqual(22, len(choices["20150217"]))

    def test_monday_available_before_11_on_saturday(self):
        with override_current_time(datetime.datetime(2015, 5, 9, 10, 30)):
            form = Mock()
            field = DayChoiceField()
            field = field.bind(form, "day")
            self.assertDayInChoices("20150511", field.choices)

        with override_current_time(datetime.datetime(2015, 5, 23, 10, 30)):
            form = Mock()
            field = DayChoiceField()
            field = field.bind(form, "day")
            self.assertDayInChoices("20150526", field.choices)

    def test_available_days(self):
        with override_current_time(datetime.datetime(2015, 5, 23, 10, 30)):
            days = OPERATOR_HOURS.available_days()
            self.assertIn(datetime.datetime(2015, 5, 26, 10, 30), days)


class TestCallbackInPastBug(FlaskAppTestCase):
    """
    Had 2 cases in which callbacks were requested in the past:
    EU-5247-5578 created 2015-02-11 23:03 for 2015-02-11 10:30
    YJ-4697-7619 created 2015-02-11 22:19 for 2015-02-11 11:00
    """

    def test_EU_5247_5578(self):
        with override_current_time(datetime.datetime(2015, 2, 11, 23, 3)):
            form = ContactForm()
            self.assertEqual([], form.callback.time.form.time_today.choices)

    def test_YJ_4697_7619(self):
        with override_current_time(datetime.datetime(2015, 2, 11, 22, 19)):
            form = ContactForm()
            self.assertEqual([], form.callback.time.form.time_today.choices)


class TestTimeChoiceField(unittest.TestCase):
    def setUp(self):
        self.form = Form()
        formdata = ImmutableMultiDict([("a", "1930")])
        with override_current_time(datetime.datetime(2015, 2, 11, 23, 3)):
            field = TimeChoiceField(choices_callback=OPERATOR_HOURS.time_slots, validators=[InputRequired()])
            self.field = field.bind(self.form, "a")
            self.field.process(formdata)

    def test_process_valid(self):
        # one of the options should be selected
        self.assertTrue(any([x[2] for x in self.field.iter_choices()]))

    def test_data_is_time_object(self):
        self.assertTrue(isinstance(self.field.data, datetime.time))

    class TestAvailabilityCheckerField(FlaskAppTestCase):
        # We are beyond the last time slot for the day
        # there should not be any call back today options
        def test_end_of_day_no_today_option(self):
            with override_current_time(datetime.datetime(2015, 5, 6, 19, 30)):
                form = CallBackForm()
                field = form.time
                # time_today should not have any values in choices so won't be displayed
                time_today_field = getattr(field.form, "time_today")
                self.assertEqual(len(time_today_field.choices), 0)
