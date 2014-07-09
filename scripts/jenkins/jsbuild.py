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

FNULL = open(os.devnull, 'w')

print 'starting...'
run('pkill -f envs/cla_.*integration', ignore_rc=True)

PROJECT_NAME = "cla_public"
BACKEND_PROJECT_NAME = "cla_backend"

SAUCELAB_BROWSERS = [
    'chrome34win81',
    'ie9win7',
]

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
run("%s/python manage.py collectstatic --noinput" % bin_path)

# run tests
backend_process = run_bg(
    ("cd %s && %s/python manage.py "
     "testserver test_outcome_codes.json initial_category.json "
     "test_provider.json test_auth_clients.json --addrport 8000 --noinput "
     "--settings=cla_backend.settings.jenkins") % (
        backend_workspace.replace(' ', '\ '), backend_bin_path),
    stdout=FNULL
)
run("wget http://localhost:8000/admin/ -t 20 "
    "--retry-connrefused --waitretry=2 -T 60")

public_process = run_bg(
    "%s/python manage.py runserver 8001" % bin_path,
    stdout=FNULL)
run("wget http://localhost:8001/ -t 20 "
    "--retry-connrefused --waitretry=2 -T 60")

nw_env = {
    'launch_url': 'http://localhost:8001',
    'project': 'cla',
    'sauce_user': os.environ.get('SAUCE_USER'),
    'sauce_key': os.environ.get('SAUCE_KEY'),
}
nw_env_str = ' '.join(["%s=%s" % (k.upper(), v) for k, v in nw_env.items()])

# phantom
# run(("%s ./nightwatch -c "
#      "tests/javascript/nightwatch/conf/jenkins/phantomjs.json") % nw_env_str)

run("%s ./nightwatch -c tests/javascript/nightwatch-jenkins.json -e %s" % (
    nw_env_str, ",".join(SAUCELAB_BROWSERS)))


print 'exiting...'
run('pkill -f envs/cla_.*integration', ignore_rc=True)
run('pkill -f nightwatch', ignore_rc=True)
