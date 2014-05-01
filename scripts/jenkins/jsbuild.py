#!/usr/bin/env python
import argparse
import subprocess
import os
import sys
import time
import shutil
import re

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
SELENIUM_JAR_URL = "http://selenium-release.storage.googleapis.com/2.41/selenium-server-standalone-2.41.0.jar"
SELENIUM_JAR_NAME = "selenium-server-standalone-2.41.0.jar"
BROWSERSTACK_ZIP_URL = "https://www.browserstack.com/browserstack-local/BrowserStackLocal-linux-x64.zip"
BROWSERSTACK_ZIP_NAME = "BrowserStackLocal-linux-x64.zip"
BROWSERSTACK_BIN_NAME = "BrowserStackLocal"
BROWSERSTACK_BROWSER_CONFS = [
    'chrome34-win8.1',
    'ie9-win7',
]

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
if not os.path.isfile("%s/%s" % (bin_path, SELENIUM_JAR_NAME)):
    run('cd "%s" && wget %s' % (bin_path, SELENIUM_JAR_URL))

# Remove .pyc files from the project
run("find . -name '*.pyc' -delete")

# build js assets
run('npm install')
run("bower install")
run("gulp build")
run( "%s/python manage.py collectstatic --noinput" % bin_path)

# run tests
backend_process = run_bg(
    "cd %s && %s/python manage.py testserver test_outcome_codes.json initial_category.json test_provider.json test_auth_clients.json --addrport 8000 --noinput --settings=cla_backend.settings.jenkins" % (backend_workspace.replace(' ', '\ '),backend_bin_path, ))
run("wget http://localhost:8000/admin/ -t 20 --retry-connrefused --waitretry=2 -T 60")

public_process = run_bg( "%s/python manage.py runserver 8001" % bin_path)
run("wget http://localhost:8001/ -t 20 --retry-connrefused --waitretry=2 -T 60")

nw_env = {
    'src_folders': 'tests/javascript/nightwatch/integration',
    'output_folder': 'reports/phantomjs',
    'launch_url': 'http://localhost:8001',
    'project': 'cla',
    'bs_user': 'janszumiec',
    'bs_key': 'oX5YoppK12BMXdVAgWvz'
}
nw_env_str = ' '.join(["%s=%s" % (k.upper(), v) for k, v in nw_env.items()])

# phantom
run("%s ./nightwatch -c tests/javascript/nightwatch/conf/jenkins/phantomjs.json" % nw_env_str)

# Ensure BrowserStackLocal is installed
if not os.path.isfile("%s/%s" % (bin_path, BROWSERSTACK_BIN_NAME)):
    run('cd "%s" && wget %s' % (bin_path, BROWSERSTACK_ZIP_URL))
    run('cd "%s" && unzip %s' % (bin_path, BROWSERSTACK_ZIP_NAME))
    run('cd "%s" && rm %s' % (bin_path, BROWSERSTACK_ZIP_NAME))

# start Browserstack local tunnel agent
run_bg("%s/%s -force oX5YoppK12BMXdVAgWvz localhost,8001,0" % (
       bin_path, BROWSERSTACK_BIN_NAME))
time.sleep(10)

bs_processes = []
for c in BROWSERSTACK_BROWSER_CONFS:
    dest_dir = 'tests/javascript/nightwatch/integration-%s' % c
    shutil.rmtree(dest_dir, ignore_errors=True)
    shutil.copytree('tests/javascript/nightwatch/integration', dest_dir)

    for root, dirs, files in os.walk(dest_dir):
        for f in files:
            os.rename(f, re.sub(r'\.js$', '.%s.js' % c, f))

    bs_nw_env = nw_env.copy()
    bs_nw_env['src_folders'] = dest_dir
    bs_nw_env['output_folder'] = 'reports/%s' % c

    bs_nw_env_str = ' '.join(["%s=%s" % (k.upper(), v)
                             for k, v in bs_nw_env.items()])

    conf_path = 'tests/javascript/nightwatch/conf/jenkins/%s.json' % c

    bs_processes.append(
        run_bg("%s ./nightwatch -c %s" % (bs_nw_env_str, conf_path))
    )

# wait for all browserstack tests to complete before killing server processes
[p.wait() for p in bs_processes]

print 'exiting...'
run('pkill -f envs/cla_.*integration', ignore_rc=True)
run('pkill -f nightwatch', ignore_rc=True)
