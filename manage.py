#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import subprocess
import sys

from flask.ext.script import Manager, Shell, Server
import requests

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
def test(i=False):
    """Run the tests. Pass -i to run integration tests as well"""
    ignore_integration = '' if i else ' -e=*_integration.py'
    nosetests = '{venv}/bin/nosetests{integration}'.format(
        venv=VENV, integration=ignore_integration)
    run(nosetests)


def add_msgctxt(**format_kwargs):
    """add msgctxt to pot file as babel doesn't seem to correctly add this for pgettext"""
    run("sed -i '' -e 's/msgid \"{context}\"/msgctxt \"{context}\"\\\nmsgid \"{message}\"/' cla_public/translations/messages.pot".format(**format_kwargs))

@manager.command
def make_messages():
    """compile po file."""
    run('{venv}/bin/pybabel extract -F babel.cfg -k pgettext -k lazy_pgettext -k '
        'gettext -k lazy_gettext -k ugettext -k ungettext -k pugettext -k '
        'lazy_pugettext -o cla_public/translations/messages.pot'
        ' .'.format(venv=VENV))

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

    for language_code, _ in app.config.get('LANGUAGES'):
        run('{venv}/bin/pybabel update -i cla_public/translations/messages.pot -d cla_public/translations -l {language_code}'
            .format(venv=VENV, language_code=language_code))


@manager.command
def push_messages():
    """Push messages to transifex"""
    # Append ' -f --no-interactive' to force push. Otherwise it wil skip if
    # the modification date on thiersw is newer
    run('tx push -s -t')


@manager.command
def pull_messages():
    """Pull messages to transifex"""
    run('tx pull')


@manager.command
def compile_messages():
    """compile po file."""
    run('{venv}/bin/pybabel compile -d cla_public/translations'.format(venv=VENV))


@manager.command
def download_means_test():
    file_path = os.path.join(os.path.dirname(__file__), 'cla_public', 'apps',
                             'checker', 'tests', 'data', 'means_test.xlsx')
    spreadsheet_id = '1idIleO4-mNTM0pW6-aOcMwXgK_0yjrpL7YkHHeuWL5c'
    response = requests.get(
        'https://docs.google.com/spreadsheets/d/%s/export?format=xlsx' %
        spreadsheet_id)
    assert response.status_code == 200, 'Wrong status code'
    s = file(file_path, 'w')
    s.write(response.content)
    s.close()


def _make_context():
    return {'app': app}


manager.add_command('server', Server())
manager.add_command('shell', Shell(make_context=_make_context))


if __name__ == '__main__':
    manager.run()
