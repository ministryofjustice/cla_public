from unittest import TestCase
from django.core.exceptions import ValidationError
from ..fields import RadioBooleanField, MoneyField


class RadioBooleanFieldsTests(TestCase):
    def test_radiobooleanfield_rejects_bad_input(self):
        f = RadioBooleanField()
        self.assertFalse(f.valid_value('aif'), msg='RadioBooleanField is allowing bad input')


    def test_radiobooleanfield_required_with_no_input_doesnt_validate(self):
        f = RadioBooleanField(required=True)
        with self.assertRaises(ValidationError):
            f.validate('')

    def test_radiobooleanfield_notrequired_with_no_input_doesnt_validate(self):
        f = RadioBooleanField(required=False)
        self.assertFalse(f.validate(''))

    def test_radiobooleanfield_with_vaild_input_validates(self):
        f = RadioBooleanField()
        self.assertTrue(f.valid_value(u'0'))
        self.assertTrue(f.valid_value(u'1'))
        self.assertTrue(f.valid_value(0))
        self.assertTrue(f.valid_value(1))
        self.assertTrue(f.valid_value(True))
        self.assertTrue(f.valid_value(False))

class MoneyFieldTests(TestCase):

    def test_clean_input(self):
        f = MoneyField()
        cleaned = f.clean('100.05')
        self.assertEqual(cleaned, 10005)

    def test_clean_input_more_than_2dp(self):
        f = MoneyField()
        cleaned = f.clean('100.049')
        self.assertEqual(cleaned, 10005)

    def test_no_input_not_valid(self):
        f = MoneyField()
        with self.assertRaises(ValidationError):
            f.clean('')

    def test_violate_min_value_input_not_allowed(self):
        f = MoneyField(min_value=0)
        with self.assertRaises(ValidationError):
            print f.clean('-24.5')

    def test_violate_max_value_input_not_allowed(self):
        f = MoneyField(max_value=40)
        with self.assertRaises(ValidationError):
            print f.clean('41')

    def test_with_valid_validates(self):
        f = MoneyField(min_value=None, max_value=None)

        self.assertEqual(2000, f.clean('20'))
        self.assertEqual(-2000, f.clean('-20'))
        self.assertEqual(0, f.clean(0))
        self.assertEqual(2000, f.clean(20))
        self.assertEqual(2050, f.clean(20.5))
        self.assertEqual(-100, f.clean(-1))


    def test_with_invalid_values_raises_validation_error(self):
        f = MoneyField()
        with self.assertRaises(ValidationError):
            f.clean('abc')
        with self.assertRaises(ValidationError):
            f.clean('?')
        with self.assertRaises(ValidationError):
            f.clean(None)
        with self.assertRaises(ValidationError):
            f.clean(True)
        with self.assertRaises(ValidationError):
            f.clean(False)
        with self.assertRaises(ValidationError):
            print f.clean('0x24C')

