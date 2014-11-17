#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import shlex
import subprocess
import sys

from flask_script import Manager, Shell, Server

from cla_public.app import create_app

log = logging.getLogger(__name__)
os.environ.setdefault('CLA_PUBLIC_CONFIG', 'config/base.py')
app = create_app()
manager = Manager(app)


def _make_context():
    return {'app': app}


@manager.command
def test():
    """Run the tests."""
    command_line = 'nosetests'
    log.info('Running %r', command_line)
    args = shlex.split(command_line)
    subprocess.Popen(args, stdin=sys.stdin,
                     stdout=sys.stdout, stderr=sys.stderr).wait()


manager.add_command('server', Server())
manager.add_command('shell', Shell(make_context=_make_context))


if __name__ == '__main__':
    manager.run()
