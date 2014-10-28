# -*- coding: utf-8 -*-
import logging
import logging.config

import sys
import os
import yaml
from flask import Flask

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

def create_app(config_name='FLASK'):
    app = Flask(__name__)
    setup_logging(bool(os.environ.get(VERBOSE_LOGGING_ENV_NAME, False)))
    setup_config(app, config_name)
    return app
