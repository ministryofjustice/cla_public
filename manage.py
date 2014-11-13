#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import shlex
import subprocess
import sys

from flask_script import Manager, Shell, Server
from flask_migrate import MigrateCommand

from cla_public.app import create_app

log = logging.getLogger(__name__)
app = create_app()
manager = Manager(app)

def _make_context():
    return {'app': app}

@manager.command
def test():
    """Run the tests."""
    command_line = app.config['NOSE_COMMAND']
    log.info('Running %r', command_line)
    args = shlex.split(command_line)
    subprocess.Popen(args, stdin=sys.stdin,
                     stdout=sys.stdout, stderr=sys.stderr).wait()

manager.add_command('server', Server())
manager.add_command('shell', Shell(make_context=_make_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
