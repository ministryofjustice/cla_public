#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import subprocess
import sys

from flask.ext.script import Manager, Shell, Server

from cla_public.app import create_app


log = logging.getLogger(__name__)
os.environ.setdefault('CLA_PUBLIC_CONFIG', 'config/base.py')
app = create_app()
manager = Manager(app)


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
        venv=os.environ.get('VIRTUAL_ENV', ''))
    run(nosetests)


def _make_context():
    return {'app': app}

manager.add_command('server', Server())
manager.add_command('httpsserver', Server(ssl_context='adhoc'))
manager.add_command('shell', Shell(make_context=_make_context))


if __name__ == '__main__':
    manager.run()
