from cla_public.apps.checker.constants import PASSPORTED_BENEFITS, \
    NASS_BENEFITS


def passported(benefits):
    return bool(set(benefits).intersection(PASSPORTED_BENEFITS))


def nass(benefits):
    return bool(set(benefits).intersection(NASS_BENEFITS))
