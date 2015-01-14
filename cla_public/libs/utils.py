import contextlib
from collections import Mapping
from flask import current_app, request
from flask.ext.babel import refresh


def get_locale():
    if request and request.cookies.get('welsh'):
        return 'cy'
    language_keys = [key for key, _ in current_app.config.get('LANGUAGES')]
    return request.accept_languages.best_match(
        language_keys
    ) or 'en'


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
            orig[key] = (orig.get('key', []) + val)
        else:
            orig[key] = new[key]
    return orig
