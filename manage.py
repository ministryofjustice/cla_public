#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import pytest

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
    import pytest
    exit_code = pytest.main(['tests', '--verbose'])
    return exit_code

manager.add_command('server', Server())
manager.add_command('shell', Shell(make_context=_make_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
