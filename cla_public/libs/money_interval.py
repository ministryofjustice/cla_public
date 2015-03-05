from decimal import Decimal, InvalidOperation

from cla_common.money_interval.models import MoneyInterval as MIBase


class MoneyInterval(dict):

    def __init__(self, *args, **kwargs):
        super(MoneyInterval, self).__init__({
            'per_interval_value': None,
            'interval_period': 'per_month'
        })

        if len(args) > 0:
            value = args[0]
            if isinstance(value, MoneyInterval):
                self.amount = value.amount
                self.interval = value.interval
            elif isinstance(value, dict):
                self.amount = value.get('per_interval_value')
                if 'interval_period' in value:
                    interval = value.get('interval_period')
                    if interval:
                        self.interval = interval
            else:
                self.amount = value

            if len(args) > 1:
                self.interval = args[1]

        else:
            self.amount = kwargs.get('per_interval_value')
            self.interval = kwargs.get('interval_period', 'per_month')

    @property
    def amount(self):
        return self.get('per_interval_value')

    @amount.setter
    def amount(self, value):
        """
        Assumes integer is amount in pence, float or Decimal is amount in
        pounds and first 2 decimal places are pence. String is converted to
        Decimal first.
        """

        try:
            if value is None:
                self['per_interval_value'] = None

            elif isinstance(value, basestring):
                self.amount = Decimal(value)

            elif isinstance(value, float):
                self.amount = int(value * 100)

            elif isinstance(value, Decimal):
                self.amount = int(value * 100)

            else:
                self['per_interval_value'] = int(value)

        except (InvalidOperation, ValueError):
            raise ValueError(
                'Invalid value for amount {0} ({1})'.format(
                    value, type(value)))

    @property
    def interval(self):
        return self.get('interval_period')

    @interval.setter
    def interval(self, value):
        if value is not None:
            if value in MIBase._intervals_dict:
                self['interval_period'] = value
            else:
                raise ValueError(value)

    def __add__(self, other):
        if other == 0:
            other = MoneyInterval(0)

        if not isinstance(other, MoneyInterval):
            raise ValueError(other)

        first = self.per_month()
        second = other.per_month()

        return MoneyInterval(first.amount + second.amount)

    def __radd__(self, other):
        return self.__add__(other)

    def per_month(self):
        if self.amount is None or self.interval == '':
            return MoneyInterval(0)

        if self.interval == 'per_month':
            return self

        multiplier = MIBase._intervals_dict[self.interval]['multiply_factor']

        return MoneyInterval(int(self.amount * multiplier))

    @classmethod
    def is_money_interval(cls, other):
        if hasattr(other, 'keys') and callable(other.keys):
            keys = set(other.keys())
            return keys == set(['per_interval_value', 'interval_period'])
        return False
