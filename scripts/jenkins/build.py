#!/usr/bin/env python
import argparse
import subprocess
import os
import sys

PROJECT_NAME = "cla_public"

# use python scripts/jenkins/build.py integration

# args
parser = argparse.ArgumentParser(description='Build project ready for testing by Jenkins.')
parser.add_argument('envname', metavar='envname', type=str, nargs=1, help='e.g. integration, production, etc.')
args = parser.parse_args()

env = args.envname[0]
env_name = "%s-%s" % (PROJECT_NAME, env)
env_path = "/tmp/jenkins/envs/%s" % env_name
bin_path = "%s/bin" % env_path


def run(command, **kwargs):
	defaults = {
		'shell': True
	}
	defaults.update(kwargs)

	return_code = subprocess.call(command, **defaults)
	if return_code:
		sys.exit(return_code)

# setting up virtualenv
if not os.path.isdir(env_path):
	run('virtualenv --no-site-packages %s' % env_path)

run('%s/pip install -r requirements/jenkins.txt' % bin_path)


# Remove .pyc files from the project
run("find . -name '*.pyc' -delete")

# run tests
run("%s/python manage.py jenkins --coverage-rcfile=.coveragerc --settings=cla_public.settings.jenkins" % bin_path)
