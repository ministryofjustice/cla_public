#!/usr/bin/env python
import argparse
import subprocess
import os
import sys

def run(command, ignore_rc=False, **kwargs):
    defaults = {
        'shell': True
    }
    defaults.update(kwargs)

    return_code = subprocess.call(command, **defaults)
    if return_code:
        if not ignore_rc:
            sys.exit(return_code)


def run_bg(command, **kwargs):
    defaults = {
        'shell': True
    }
    defaults.update(kwargs)

    return subprocess.Popen(command, **defaults)


print 'starting...'
run('pkill -f envs/cla_.*integration', ignore_rc=True)

PROJECT_NAME = "cla_public"
BACKEND_PROJECT_NAME = "cla_backend"
SELENIUM_ZIP_NAME = "selenium-java-2.41.0.zip"
SELENIUM_UNZIP_DIR = "selenium-2.41.0"
SELENIUM_ZIP_URL = "http://selenium-release.storage.googleapis.com/2.41/%s" % SELENIUM_ZIP_NAME
SELENIUM_JAR_NAME = "selenium-java-2.41.0.jar"

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

# Install Selenium .jar if not already present
if not os.path.isfile("%s/%s" % (backend_workspace, SELENIUM_JAR_NAME)):
    if not os.path.isfile("%s/%s" % (backend_workspace, SELENIUM_ZIP_NAME)):
        run('cd "%s" && wget %s' % (backend_workspace, SELENIUM_ZIP_URL))
    run('rm -rf "%s/%s"' % (backend_workspace, SELENIUM_UNZIP_DIR))
    run('cd "%s" && unzip %s' % (backend_workspace, SELENIUM_ZIP_NAME))
    run('cd "%s" && mv "%s/%s" "%s"' % (backend_workspace, SELENIUM_UNZIP_DIR,
                                        SELENIUM_JAR_NAME, backend_workspace))

# Remove .pyc files from the project
run("find . -name '*.pyc' -delete")

# build js assets
run('npm install')
run("bower install")
run("gulp build")
run( "%s/python manage.py collectstatic --noinput" % bin_path)

# run tests
backend_process = run_bg(
    "cd %s && %s/python manage.py testserver initial_category.json test_auth_clients.json --addrport 8000 --noinput --settings=cla_backend.settings.jenkins" % (backend_workspace.replace(' ', '\ '),backend_bin_path, ))
run("wget http://localhost:8000/admin/ -t 20 --retry-connrefused --waitretry=2 -T 60")

public_process = run_bg( "%s/python manage.py runserver 8001" % bin_path)
run("wget http://localhost:8001/ -t 20 --retry-connrefused --waitretry=2 -T 60")

run('make test-jenkins')

print 'exiting...'
run('pkill -f envs/cla_.*integration', ignore_rc=True)
