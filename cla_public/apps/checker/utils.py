from cla_public.apps.checker.constants import PASSPORTED_BENEFITS, \
    NASS_BENEFITS, MONEY_INTERVALS


def passported(benefits):
    return bool(set(benefits).intersection(PASSPORTED_BENEFITS))


def nass(benefits):
    return bool(set(benefits).intersection(NASS_BENEFITS))


def money_intervals_except(*fields):
    return [(key, display) for key, display in MONEY_INTERVALS if key not in fields]


def money_intervals(*fields):
    return [(key, display) for key, display in MONEY_INTERVALS if key in fields]
