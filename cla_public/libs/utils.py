import contextlib
import logging
from collections import Mapping

from flask import current_app, request
from flask.ext.babel import refresh

from cla_public.apps.checker.constants import CATEGORIES

log = logging.getLogger(__name__)


class classproperty(object):
    """
    A decorator for a class method to make it appear to be a class property
    """

    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


def get_locale():
    if request and request.cookies.get("locale"):
        return request.cookies.get("locale")[:2]
    language_keys = [key for key, _ in current_app.config.get("LANGUAGES", {})]
    return request.accept_languages.best_match(language_keys) or "en"


@contextlib.contextmanager
def override_locale(locale):
    def set_locale_selector_func(fn):
        current_app.babel.locale_selector_func = None
        current_app.babel.localeselector(fn)
        refresh()

    original = current_app.babel.locale_selector_func
    set_locale_selector_func(lambda: locale)
    yield
    set_locale_selector_func(original)


def recursive_dict_update(orig, new):
    """
    Update dict with new dict by recursively merging dictionaries
    :param orig: dict - original dict
    :param new: dict - updated values
    :return: dict
    """
    for key, val in new.iteritems():
        if isinstance(val, Mapping):
            tmp = recursive_dict_update(orig.get(key, {}), val)
            orig[key] = tmp
        elif isinstance(val, list):
            orig[key] = orig.get("key", []) + val
        else:
            orig[key] = new[key]
    return orig


def log_to_sentry(message):
    try:
        current_app.sentry.captureMessage(message)
    except AttributeError:
        log.warning(message)


def flatten_dict(prefix, data_dict):
    return {"%s-%s" % (prefix, key): val for key, val in data_dict.items()}


def flatten_list(prefix, data_list):
    out = {}
    for num, d in enumerate(data_list):
        p = "%s-%s" % (prefix, num)
        if isinstance(d, Mapping):
            out.update(flatten_dict(p, d))
        elif isinstance(d, list):
            out.update(flatten_list(p, d))
        else:
            out.update({d: True})
    return out


def flatten(dict_, prefix=""):
    out = {}
    for key, val in dict_.items():
        new_prefix = "-".join(filter(lambda x: x, [prefix, key]))
        if isinstance(val, Mapping):
            out.update(flatten(flatten_dict(new_prefix, val)))
        elif isinstance(val, list) and not (len(val) > 0 and isinstance(val[0], basestring)):
            out.update(flatten(flatten_list(new_prefix, val)))
        else:
            out.update({new_prefix: val})
    return out


def category_id_to_name(category_id):
    selected_name = lambda (slug, name, _): slug == category_id and name  # noqa: E731
    selected = filter(None, map(selected_name, CATEGORIES))
    return selected[0] if selected else None
