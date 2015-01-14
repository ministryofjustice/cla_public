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

def add_msgctxt(**format_kwargs):
    """add msgctxt to pot file as babel doesn't seem to correctly add this for pgettext"""
    run("sed -i '' -e 's/msgid \"{context}\"/msgctxt \"{context}\"\\\nmsgid \"{message}\"/' cla_public/translations/messages.pot".format(**format_kwargs))

@manager.command
def make_messages():
    """compile po file."""
    run('{venv}/bin/pybabel extract -F babel.cfg -k pgettext -k lazy_pgettext -k '
        'gettext -k lazy_gettext -o cla_public/translations/messages.pot .'.format(venv=VENV))

    pgettexts = [
        {'context': 'There is\/are', 'message': 'Yes'},
        {'context': 'There is\/are not', 'message': 'No'},
        {'context': 'It is', 'message': 'Yes'},
        {'context': 'It isn’t', 'message': 'No'},
        {'context': 'I am', 'message': 'Yes'},
        {'context': 'I’m not', 'message': 'No'},
    ]
    for trans in pgettexts:
        add_msgctxt(**trans)

    run('cat cla_public/translations/wtforms.pot >> cla_public/translations/messages.pot')
    for language_code, _ in app.config.get('LANGUAGES'):
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
