from cla_public.apps.checker.constants import PASSPORTED_BENEFITS, \
    NASS_BENEFITS, MONEY_INTERVALS, CATEGORIES


def passported(benefits):
    return bool(set(benefits).intersection(PASSPORTED_BENEFITS))


def nass(benefits):
    if benefits:
        return bool(set(benefits).intersection(NASS_BENEFITS))
    return False


def money_intervals_except(*fields):
    return [(key, display) for key, display in MONEY_INTERVALS if key not in fields]


def money_intervals(*fields):
    return [(key, display) for key, display in MONEY_INTERVALS if key in fields]


def category_option_from_name(category_name):
    requested = lambda (slug, name, desc): name == category_name  # noqa: E731
    return next(
        iter(filter(requested, CATEGORIES)),
        (None, None, None))
