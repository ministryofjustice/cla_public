#!/usr/bin/env python
import argparse
import logging
import os
import signal
import subprocess
import sys
from Queue import Queue


logging.basicConfig(level='INFO')
log = logging.getLogger(__name__)

PROJECT_NAME = "cla_public"

background_processes = Queue()


def env_name():
    parser = argparse.ArgumentParser(
        description='Build project ready for testing by Jenkins.')
    parser.add_argument(
        'envname',
        metavar='envname',
        type=str,
        nargs=1,
        help='e.g. integration, production, etc.')
    args = parser.parse_args()
    return args.envname[0]


def run(command, background=False, **kwargs):
    if 'shell' not in kwargs:
        kwargs['shell'] = True

    log.info('Running {command}'.format(command=command))

    if background:
        process = subprocess.Popen(command, **kwargs)
        background_processes.put(process)
        return process

    return_code = subprocess.call(command, **kwargs)
    if return_code:
        sys.exit(return_code)


def make_virtualenv(env):
    venv_path = '/tmp/jenkins/envs/{project}-{env}'.format(
        project=PROJECT_NAME,
        env=env)

    if not os.path.isdir(venv_path):
        run('virtualenv --no-site-packages {path}'.format(path=venv_path))

    return venv_path


def install_dependencies(venv_path):
    run('{venv}/bin/pip install -r requirements/jenkins.txt'.format(
        venv=venv_path))
    run('npm install')
    run('bower install')


def clean_pyc():
    run("find . -name '*.pyc' -delete")


def run_tests(venv_path):
    config = 'CLA_PUBLIC_CONFIG=config/jenkins.py'
    run('{conf} {venv}/bin/nosetests --with-xunit'.format(
        venv=venv_path,
        conf=config))
    run('{conf} {venv}/bin/python manage.py runserver'.format(venv=venv_path),
        background=True)
    run('./nightwatch -c tests/nightwatch/public-integration.json')


def kill_child_processes(pid, sig=signal.SIGTERM):
    ps_cmd = subprocess.Popen(
        'ps -o pid --ppid {0} --noheaders'.format(pid),
        shell=True,
        stdout=subprocess.PIPE)
    ps_out = ps_cmd.stdout.read()
    retcode = ps_cmd.wait()
    for pid_str in ps_out.split('\n')[:-1]:
        os.kill(int(pid_str), sig)


def main():
    try:
        venv_path = make_virtualenv(env_name())
        install_dependencies(venv_path)
        clean_pyc()
        run_tests(venv_path)
    finally:
        while not background_processes.empty():
            process = background_processes.get()
            try:
                kill_child_processes(process.pid)
                process.kill()
            except OSError:
                pass


if __name__ == '__main__':
    main()
