#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import subprocess
import sys

from flask.ext.script import Manager, Shell, Server

from cla_public.app import create_app


log = logging.getLogger(__name__)
os.environ.setdefault('CLA_PUBLIC_CONFIG', 'config/common.py')
app = create_app()
manager = Manager(app)

VENV = os.environ.get('VIRTUAL_ENV', '')


def run(command, **kwargs):
    if 'shell' not in kwargs:
        kwargs['shell'] = True

    return_code = subprocess.call(command, **kwargs)
    if return_code:
        sys.exit(return_code)


@manager.command
def test():
    """Run the tests."""
    nosetests = '{venv}/bin/nosetests'.format(
        venv=VENV)
    run(nosetests)


@manager.command
def make_messages():
    """compile po file."""
    run('{venv}/bin/pybabel extract -F babel.cfg -k lazy_gettext -o cla_public/translations/messages.pot .'.format(venv=VENV))
    for language_code in app.config.get('LANGUAGES').keys():
        run('{venv}/bin/pybabel update -i cla_public/translations/messages.pot -d cla_public/translations -l {language_code}'
            .format(venv=VENV, language_code=language_code))


@manager.command
def compile_messages():
    """compile po file."""
    run('{venv}/bin/pybabel compile -d cla_public/translations'.format(venv=VENV))


def _make_context():
    return {'app': app}


manager.add_command('server', Server())
manager.add_command('shell', Shell(make_context=_make_context))


if __name__ == '__main__':
    manager.run()
