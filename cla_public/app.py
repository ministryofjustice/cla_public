# -*- coding: utf-8 -*-
import logging
import logging.config
import jinja2
import sys
import os
import yaml
from flask import Flask, url_for, Blueprint, render_template

from cla_public.views.index import base_blueprint
from cla_public.views.problem import problem_blueprint

log = logging.getLogger(__name__)


# Name of the environment variable that we read the config file from
CONFIG_FILE_ENV_NAME = 'CLA_PUBLIC_CONFIG'

# Name of the environment variable that we determine the verbosity of
# the logger.
VERBOSE_LOGGING_ENV_NAME = 'CLA_PUBLIC_VERBOSE'

def setup_logging(verbose=False):
    try:
        with open('logging.conf') as f:
            logging.config.dictConfig(yaml.load(f.read()))
    except (yaml.YAMLError, yaml.MarkedYAMLError, IOError):
        if verbose:
            level = logging.DEBUG
        else:
            level = logging.INFO

        logging.basicConfig(level=level,
                            format='%(asctime)s %(levelname)-8s %(name)s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')

        # logging for the cla_public module (top level)
        logger = logging.getLogger('cla_public')
        logger.setLevel(level)


def setup_config(app, config_name):
    """Initialises the configuration for a Flask application.

    After that, the environment variable CONFIG_FILE_ENV_NAME is
    consulted, and its value, which must point to a Python file either
    absolutely or relative to the root of the project."""
    try:
        user_config_file = os.environ[CONFIG_FILE_ENV_NAME]
        if not os.path.isfile(user_config_file):
            log.critical('Config file %s is not a valid file. Exiting...', user_config_file)
            sys.exit(1)
        else:
            try:
                with open(user_config_file) as f:
                    config_data = yaml.load(f.read())
                app.config.update(config_data[config_name])
                log.info('Loaded configuration file %s', user_config_file)
            except (yaml.YAMLError, yaml.MarkedYAMLError):
                log.exception('Parsing YAML file %s failed. Exiting...', user_config_file)
                sys.exit(1)
    except KeyError:
        log.critical('Environment variable %s must be set. Exiting...', CONFIG_FILE_ENV_NAME)
        sys.exit(1)

def change_jinja_templates(app):
    # Change the template loader so it will seek out the MOJ Jinja
    # base templates.
    moj_loader = jinja2.ChoiceLoader([
            app.jinja_loader,
            jinja2.PackageLoader('moj_template', 'templates'),
            ])

    app.jinja_loader = moj_loader

    # we need to load a special method called "static" to mimic
    # Django; ideally we would not rely on Django-isms but the MOJ
    # template assumes you're using jinja with Django.
    import moj_template
    root_template_dir = moj_template.__path__[0]
    static_dir = os.path.join(root_template_dir, 'static')
    template_dir = os.path.join(root_template_dir,
                                'templates', 'moj_template')

    moj_template_blueprint = Blueprint('moj_template', 'moj_template',
                                       static_folder=static_dir,
                                       static_url_path='/moj-static',
                                       template_folder=template_dir)
    app.register_blueprint(moj_template_blueprint)

    @app.context_processor
    def utility_processor():
        def static(filename):
            return url_for('moj_template.static', filename=filename)
        return {'static': static}

    # Expose user variables
    @app.context_processor
    def moj_variables():
        try:
            return app.config['APP_SETTINGS']
        except KeyError:
            log.critical('Cannot find APP_SETTINGS group in the configuration file.')
            sys.exit(1)
    return app

def register_error_handlers(app):
    @app.errorhandler(404)
    def http_page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def http_server_error(e):
        return render_template('500.html'), 500

    return app

def create_app(config_name='FLASK'):
    app = Flask(__name__)
    # This should happen before other things
    app.register_blueprint(base_blueprint)
    app.register_blueprint(problem_blueprint)
    setup_logging(bool(os.environ.get(VERBOSE_LOGGING_ENV_NAME, False)))
    setup_config(app, config_name)
    app = change_jinja_templates(app)
    app = register_error_handlers(app)
    return app
