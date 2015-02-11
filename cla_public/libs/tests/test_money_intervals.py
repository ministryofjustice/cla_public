import unittest

from cla_public.libs.money_interval import MoneyInterval


class TestMoneyInterval(unittest.TestCase):

    def test_init_empty(self):
        mint = MoneyInterval()
        self.assertEqual(None, mint.amount)
        self.assertEqual('per_month', mint.interval)

    def test_init_from_integer(self):
        mint = MoneyInterval(100)
        self.assertEqual(100, mint.amount)
        self.assertEqual('per_month', mint.interval)

    def test_init_from_integer_and_string(self):
        mint = MoneyInterval(100, 'per_week')
        self.assertEqual(100, mint.amount)
        self.assertEqual('per_week', mint.interval)

    def test_init_from_money_interval_dict(self):
        mint = MoneyInterval({
            'per_interval_value': 100,
            'interval_period': 'per_week'})
        self.assertEqual(100, mint.amount)
        self.assertEqual('per_week', mint.interval)

    def test_init_from_money_interval(self):
        mint_a = MoneyInterval(1)
        mint_b = MoneyInterval(mint_a)
        self.assertEqual(1, mint_b.amount)

    def test_init_from_invalid(self):
        with self.assertRaises(ValueError):
            mint = MoneyInterval('foo')

    def test_init_invalid_interval(self):
        with self.assertRaises(ValueError):
            mint = MoneyInterval(0, 'per_century')

    def test_init_from_kwargs(self):
        mint = MoneyInterval(
            interval_period='per_week',
            per_interval_value=500)
        self.assertEqual(500, mint.amount)
        self.assertEqual('per_week', mint.interval)

    def test_setters(self):
        mint = MoneyInterval()
        mint.amount = 100
        mint.interval = 'per_week'
        self.assertEqual(100, mint.amount)
        self.assertEqual('per_week', mint.interval)

    def test_normalize_to_per_month(self):
        mint = MoneyInterval(100, 'per_week')
        mint = mint.per_month()
        self.assertEqual(433, mint.amount)
        self.assertEqual('per_month', mint.interval)

    def test_add(self):
        mint_a = MoneyInterval(1)
        mint_b = MoneyInterval(2)
        mint_c = mint_a + mint_b
        self.assertEqual(3, mint_c.amount)
        self.assertEqual('per_month', mint_c.interval)

    def test_add_different_intervals(self):
        mint_a = MoneyInterval(100, 'per_week')
        mint_b = MoneyInterval(100, 'per_month')
        mint_c = mint_a + mint_b
        self.assertEqual(533, mint_c.amount)
        self.assertEqual('per_month', mint_c.interval)

    def test_add_invalid(self):
        mint = MoneyInterval(100)
        with self.assertRaises(ValueError):
            mint = mint + 1

    def test_sum(self):
        mints = map(MoneyInterval, range(1, 4))
        total = sum(mints)
        self.assertEqual(6, total.amount)
        self.assertEqual('per_month', total.interval)

    def test_add_zero(self):
        mint = MoneyInterval(3)
        total = 0 + mint
        self.assertEqual(3, total.amount)
        self.assertEqual('per_month', total.interval)
        total = mint + 0
        self.assertEqual(3, total.amount)
        self.assertEqual('per_month', total.interval)
