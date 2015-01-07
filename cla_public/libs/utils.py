import contextlib
from flask import current_app, request
from flask.ext.babel import refresh


def get_locale():
    language_keys = current_app.config.get('LANGUAGES').keys()
    # make english the first choice (dicts have no order)
    language_keys.insert(0, language_keys.pop(language_keys.index('en')))
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
