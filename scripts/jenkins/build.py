#!/usr/bin/env python
import argparse
import subprocess
import os
import sys


PROJECT_NAME = 'cla_public'


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


def run(command, **kwargs):
    if 'shell' not in kwargs:
        kwargs['shell'] = True

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


def clean_pyc():
    run("find . -name '*.pyc' -delete")


def run_tests(config, venv_path):
    run((
        'CLA_PUBLIC_CONFIG={config} {venv}/bin/python manage.py jenkins '
        '--coverage-rcfile=.coveragerc '
        '--settings=cla_callmeback.settings.jenkins').format(
            config=config,
            venv=venv_path))


def config_module(env):
    return 'config.{env}'.format(env=env)


def main():
    env = env_name()
    venv_path = make_virtualenv(env)
    install_dependencies(venv_path)
    clean_pyc()
    run_tests(config_module(env), venv_path)


if __name__ == '__main__':
    main()
