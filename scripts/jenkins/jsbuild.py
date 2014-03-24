#!/usr/bin/env python
import argparse
import subprocess
import os
import sys


def run(command, **kwargs):
    defaults = {
        'shell': True
    }
    defaults.update(kwargs)

    return_code = subprocess.call(command, **defaults)
    if return_code:
        sys.exit(return_code)


def run_bg(command, **kwargs):
    defaults = {
        'shell': True
    }
    defaults.update(kwargs)

    return_code = subprocess.Popen(command, **defaults)
    if return_code:
        sys.exit(return_code)



PROJECT_NAME = "cla_public"
BACKEND_PROJECT_NAME = "cla_backend"

# use python scripts/jenkins/build.py integration

# args
parser = argparse.ArgumentParser(
    description='Build project ready for testing by Jenkins.')
parser.add_argument('envname', metavar='envname', type=str, nargs=1,
                    help='e.g. integration, production, etc.')

parser.add_argument('--backend-dir', metavar='backend_dir', type=str, nargs=1,
                    help='path to backend project')
args = parser.parse_args()

env = args.envname[0]
backend_workspace = args.backend_dir[0]

env_name = "%s-%s" % (PROJECT_NAME, env)
env_path = "/tmp/jenkins/envs/%s" % env_name
bin_path = "%s/bin" % env_path

backend_env_name = "%s-%s" % (BACKEND_PROJECT_NAME, env)
backend_env_path = "/tmp/jenkins/envs/%s" % backend_env_name
backend_bin_path = "%s/bin" % backend_env_path


# Remove .pyc files from the project
run("find . -name '*.pyc' -delete")

# build js assets
run('npm install')
run("bower install")
run("gulp build")
run( "%s/python manage.py collectstatic --noinput" % bin_path)

# run tests
backend_process = run_bg(
    "%s/python %s/manage.py testserver initial_category.json --addport 8000 --noinput" % (backend_bin_path, backend_workspace.replace(' ', '\ '),))
public_process = run_bg( "%s/python manage.py runserver 8001" % bin_path)
run('make test')
backend_process.terminate()
public_process.terminate()
