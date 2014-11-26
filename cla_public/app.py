# -*- coding: utf-8 -*-
"CLA Public app"

import logging
import os
from flask import Flask, render_template
from flask.ext.cache import Cache
from raven.contrib.flask import Sentry

from cla_public.django_to_jinja import change_jinja_templates
from cla_public.apps.base.views import base
from cla_public.apps.checker.views import checker
from cla_public.apps.checker.session import CheckerSessionInterface


log = logging.getLogger(__name__)


def create_app(config_file=None):
    app = Flask(__name__)
    app = change_jinja_templates(app)
    if config_file:
        app.config.from_pyfile(config_file)
    else:
        app.config.from_envvar('CLA_PUBLIC_CONFIG')

    if app.config.get('SENTRY_DSN'):
        Sentry().init_app(app)

    for extension in app.config['EXTENSIONS']:
        extension.init_app(app)

    app.session_interface = CheckerSessionInterface()

    app.cache = Cache(app, config=app.config['CACHE_CONFIG'])

    register_error_handlers(app)

    app.register_blueprint(base)
    app.register_blueprint(checker)

    logging.basicConfig(
        level=app.config.get('LOG_LEVEL', 'DEBUG'),
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    if app.debug:
        from werkzeug.debug import DebuggedApplication
        app = DebuggedApplication(app, True)

    return app


def register_error_handlers(app):
    """
    Assign error page templates to all error status codes we care about
    """

    error_handlers = {
        '404.html': [404],
        '4xx.html': [401, 402, 405, 406, 407, 408, 409],
        '5xx.html': [500, 501, 502, 503, 504, 505]}

    def make_handler(code, template):

        def handler(e):
            return render_template(os.path.join('errors', template)), code

        return handler

    for template, codes in error_handlers.iteritems():
        for code in codes:
            app.register_error_handler(code, make_handler(code, template))

    return app
