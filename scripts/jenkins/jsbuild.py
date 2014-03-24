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

    return subprocess.Popen("exec " + command, **defaults)



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
    "cd %s && %s/python manage.py testserver initial_category.json --addrport 8000 --noinput --settings=cla_backend.settings.jenkins" % (backend_workspace.replace(' ', '\ '),backend_bin_path, ))
run("curl --connect-timeout 5 \
     --max-time 10 \
     --retry 20 \
     --retry-delay 2 \
     --retry-max-time 60 \
     'http://127.0.0.1:8000'")

public_process = run_bg( "%s/python manage.py runserver 8001" % bin_path)
run("curl --connect-timeout 5 \
     --max-time 10 \
     --retry 20 \
     --retry-delay 2 \
     --retry-max-time 60 \
     'http://127.0.0.1:8001'")


run('make test')

run('pkill -f envs/cla_.*integration')
