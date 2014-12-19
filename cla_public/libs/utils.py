from flask import current_app, request


def get_locale():
    return request.accept_languages.best_match(
        current_app.config.get('LANGUAGES').keys()
    ) or 'en'
