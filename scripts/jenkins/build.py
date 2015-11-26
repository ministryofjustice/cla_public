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

PROJECT_NAME = 'cla_public'

background_processes = Queue()


def parse_args():
    parser = argparse.ArgumentParser(
        description='Build project ready for testing by Jenkins.')
    parser.add_argument('envname', type=str,
                        help='e.g. integration, production, etc.')
    parser.add_argument('--backend-hash', type=str, default='',
                        help='cla_backend *commit hash* to run tests against; '
                             'defaults to latest develop branch commit')
    parser.add_argument('--skip-tests', type=str, default='',
                        help='Skip tests e.g. integration, unit, all')
    parser.add_argument('--test-browser', type=str, default='firefox',
                        help='e.g. firefox, chrome, phantomjs')

    return parser.parse_args()


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
        run('/usr/local/bin/virtualenv {path}'.format(path=venv_path))

    return venv_path


def install_dependencies(venv_path):
    run('{venv}/bin/pip install -U setuptools pip wheel'.format(
        venv=venv_path))
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


def remove_old_static_assets():
    run('rm -f cla_public/static-src/javascripts/templates.js')


def update_static_assets():
    run('gulp')


def compile_messages(venv_path):
    """Compile message.po files to mo files for the translations"""
    run('{venv}/bin/pybabel compile -d cla_public/translations'.format(venv=venv_path))


def _port(start_from=8300, up_to=8499):
    port = random.randint(start_from, up_to)
    while True:
        yield port
        port += 1


gen_port = _port()


def run_server(env, backend_hash, jenkins_build_path):
    venv = '/tmp/jenkins/envs/cla_backend-%s' % env
    project_dir = '/srv/jenkins/shared-backend/%s-%s' % (PROJECT_NAME, env)
    if not os.path.isdir(project_dir):
        os.makedirs(project_dir)

    if not os.path.isdir(os.path.join(project_dir, '.git')):
        run('cd {project_dir} && git clone https://github.com/ministryofjustice/cla_backend.git .'.format(
            project_dir=project_dir,
        ))
    if backend_hash:
        run('cd {project_dir} && git fetch --prune && git checkout -f {backend_hash}'.format(
            project_dir=project_dir,
            backend_hash=backend_hash,
        ))
    else:
        run('cd {project_dir} && git fetch --prune && git checkout develop && git pull'.format(
            project_dir=project_dir,
        ))

    backend_port = next(gen_port)
    os.environ['CLA_BACKEND_PORT'] = str(backend_port)
    os.environ['BACKEND_TEST_DB_SUFFIX'] = '4%s' % PROJECT_NAME

    fixtures = (
        'initial_groups.json',
        'kb_from_knowledgebase.json',
        'initial_category.json',
        'test_provider.json',
        'initial_mattertype.json',
        'test_auth_clients.json',
        'initial_media_codes.json',
        'test_rotas.json',
        'test_casearchived.json',
        'test_providercases.json',
        'test_provider_allocations.json',
        'initial_complaint_categories',
    )

    log_stdout = os.path.join(jenkins_build_path, 'cla_backend.stdout.log')
    log_stderr = os.path.join(jenkins_build_path, 'cla_backend.stderr.log')

    run(('cd {project_dir} && '
         '{venv}/bin/python manage.py testserver {fixtures} '
         '--addrport {port} --noinput '
         '--settings=cla_backend.settings.jenkins '
         '1> {log_stdout} '
         '2> {log_stderr}').format(
            project_dir=project_dir,
            venv=venv,
            fixtures=' '.join(fixtures),
            port=backend_port,
            log_stdout=log_stdout,
            log_stderr=log_stderr,
        ),
        background=True)


def run_tests(venv_path, jenkins_build_path, browser, skip_tests=''):
    run('echo {skip_tests}'.format(skip_tests=skip_tests))
    run('echo "--- RUNNING TESTS..."')
    if all(x in skip_tests for x in ['integration', 'unit']):
        run('echo "--- SKIPPED!"')
        return

    wait_until_available('http://localhost:{port}/admin/'.format(
        port=os.environ.get('CLA_BACKEND_PORT'))
    )

    config = 'CLA_PUBLIC_CONFIG=config/jenkins.py'
    public_port = next(gen_port)
    os.environ['CLA_PUBLIC_PORT'] = str(public_port)

    log_stdout = os.path.join(jenkins_build_path, 'cla_public.stdout.log')
    log_stderr = os.path.join(jenkins_build_path, 'cla_public.stderr.log')

    if skip_tests.find('unit') == -1:
        run('echo "--- UNIT"')
        run('{conf} {venv}/bin/nosetests --with-xunit'.format(
            venv=venv_path,
            conf=config))

    if 'integration' in skip_tests:
        return

    run('echo "--- INTEGRATION"')
    run((
        '{conf} {venv}/bin/python manage.py mockserver -p {port} -D -R '
        '1> {log_stdout} '
        '2> {log_stderr}').format(
            venv=venv_path,
            conf=config,
            port=public_port,
            log_stdout=log_stdout,
            log_stderr=log_stderr,
        ),
        background=True)
    wait_until_available('http://localhost:{port}/'.format(port=public_port))
    run('npm run update-selenium')
    run('./nightwatch --env {browser} -c tests/nightwatch/jenkins.json -M'.format(browser=browser))

    # nightwatch fails to clean up these process
    # NB: if two jobs are running on the same jenkins slave then one may break the other
    run('killall phantomjs || echo "No orphan phantomjs processes"')


def kill_child_processes(pid, sig=signal.SIGTERM):
    ps_cmd = subprocess.Popen(
        'ps -o pid --ppid {0} --noheaders'.format(pid),
        shell=True,
        stdout=subprocess.PIPE)
    ps_out = ps_cmd.stdout.read()
    ps_cmd.wait()
    for pid_str in ps_out.split('\n')[:-1]:
        os.kill(int(pid_str), sig)


def kill_all_background_processes():
    while not background_processes.empty():
        process = background_processes.get()
        try:
            kill_child_processes(process.pid)
            process.kill()
        except OSError:
            pass


def main():
    try:
        jenkins_workspace_path = os.environ['WORKSPACE']
        jenkins_build_path = os.path.join(jenkins_workspace_path,
                                          '..', 'builds',
                                          os.environ['BUILD_NUMBER'])
        jenkins_build_path = os.path.abspath(jenkins_build_path)

        args = parse_args()
        env = args.envname
        backend_hash = args.backend_hash
        skip_tests = args.skip_tests
        venv_path = make_virtualenv(env)
        install_dependencies(venv_path)
        remove_old_static_assets()
        update_static_assets()
        compile_messages(venv_path)
        clean_pyc()
        run_server(env, backend_hash, jenkins_build_path)
        run_tests(venv_path, jenkins_build_path,
                  browser=args.test_browser,
                  skip_tests=skip_tests)
    finally:
        kill_all_background_processes()


if __name__ == '__main__':
    main()
