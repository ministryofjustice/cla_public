# -*- coding: utf-8 -*-
"CLA Public app"

import logging
from flask import Blueprint, Flask, url_for, render_template
from flask.ext.cache import Cache
from raven.contrib.flask import Sentry

from cla_public.django_to_jinja import change_jinja_templates
from cla_public.apps.base.views import base
from cla_public.apps.checker.views import checker
from cla_public.apps.checker.session import CheckerSessionInterface


log = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(404)
    def http_page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def http_server_error(e):
        return render_template('500.html'), 500

    return app


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

    return app
