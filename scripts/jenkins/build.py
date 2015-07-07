#!/usr/bin/env python
import argparse
import logging
import os
import random
import signal
import subprocess
import sys
from Queue import Queue


logging.basicConfig(level='INFO')
log = logging.getLogger(__name__)

PROJECT_NAME = "cla_public"

background_processes = Queue()


def parse_args():
    parser = argparse.ArgumentParser(
        description='Build project ready for testing by Jenkins.')
    parser.add_argument(
        'envname',
        metavar='envname',
        type=str,
        nargs=1,
        help='e.g. integration, production, etc.')
    parser.add_argument(
        '--threshold-tests',
        action='store_true',
        help='run threshold tests')

    args = parser.parse_args()
    return {
        'envname': args.envname[0],
        'threshold_tests': args.threshold_tests}


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


def wait_until_available(url):
    wget = run((
        'wget {url} -O/dev/null -t 20 --retry-connrefused --waitretry=2 '
        '-T 60').format(url=url),
        background=True)
    wget.wait()


def remove_old_template_js():
    run('rm -f cla_public/static-src/javascripts/templates.js')


def update_static_assets():
    run('gulp')


def _port(start_from=8000, up_to=8999):
    port = random.randint(start_from, up_to)
    while True:
        yield port
        port += 1


def run_server(
        env,
        project_name='cla_backend',
        port_env_var='CLA_BACKEND_PORT',
        project_dir=None):

    if not project_dir:
        if env == 'production':
            project_dir = '/srv/jenkins/workspace/CLA Backend - production'
        else:
            project_dir = '/srv/jenkins/workspace/CLA Backend - integration'

    port = next(_port())
    os.environ[port_env_var] = '{0}'.format(port)

    venv = '/tmp/jenkins/envs/{0}-{1}'.format(project_name, env)

    fixtures = (
        'initial_groups.json '
        'kb_from_knowledgebase.json '
        'initial_category.json '
        'test_provider.json '
        'initial_mattertype.json '
        'test_auth_clients.json '
        'initial_media_codes.json '
        'test_rotas.json '
        'test_casearchived.json '
        'test_providercases.json '
        'test_provider_allocations.json')

    run((
        'cd {workspace} && '
        '{venv}/bin/python manage.py testserver {fixtures} --addrport {port} '
        '--noinput --settings=cla_backend.settings.jenkins > /dev/null').format(
            workspace=project_dir.replace(' ', '\ '),
            venv=venv,
            fixtures=fixtures,
            port=port),
        background=True)


def run_tests(venv_path, threshold_tests=False):
    config = 'CLA_PUBLIC_CONFIG=config/jenkins.py'
    port = next(_port())
    os.environ['CLA_PUBLIC_PORT'] = '{0}'.format(port)
    run('{conf} {venv}/bin/nosetests --with-xunit'.format(
        venv=venv_path,
        conf=config))
    run(
        '{conf} {venv}/bin/python manage.py mockserver -p {port} -D -R'.format(
            venv=venv_path,
            conf=config,
            port=port),
        background=True)
    wait_until_available('http://localhost:{port}/'.format(port=port))
    skipgroup = ' -s legacy'
    if threshold_tests:
        skipgroup = ''
    run('./nightwatch -c tests/nightwatch/jenkins.json{0} -M'.format(skipgroup))


def kill_child_processes(pid, sig=signal.SIGTERM):
    ps_cmd = subprocess.Popen(
        'ps -o pid --ppid {0} --noheaders'.format(pid),
        shell=True,
        stdout=subprocess.PIPE)
    ps_out = ps_cmd.stdout.read()
    retcode = ps_cmd.wait()
    for pid_str in ps_out.split('\n')[:-1]:
        os.kill(int(pid_str), sig)


def compile_messages(venv_path):
    """Compile message.po files to mo files for the translations"""
    run('{venv}/bin/pybabel compile -d cla_public/translations'.format(venv=venv_path))


def main():
    try:
        args = parse_args()
        env = args['envname']
        venv_path = make_virtualenv(env)
        install_dependencies(venv_path)
        remove_old_template_js()
        update_static_assets()
        compile_messages(venv_path)
        clean_pyc()
        run_server(env)
        wait_until_available('http://localhost:{port}/admin/'.format(
            port=os.environ.get('CLA_BACKEND_PORT')))
        run_tests(venv_path, args['threshold_tests'])
    finally:
        kill_all_background_processes()


def kill_all_background_processes():
    while not background_processes.empty():
        process = background_processes.get()
        try:
            kill_child_processes(process.pid)
            process.kill()
        except OSError:
            pass


if __name__ == '__main__':
    main()
