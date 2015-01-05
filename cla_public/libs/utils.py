from flask import current_app, request


def get_locale():
    language_keys = current_app.config.get('LANGUAGES').keys()
    # make english the first choice (dicts have no order)
    language_keys.insert(0, language_keys.pop(language_keys.index('en')))
    return request.accept_languages.best_match(
        language_keys
    ) or 'en'
