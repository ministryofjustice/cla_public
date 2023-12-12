#!/usr/bin/env bash
set -e

echo "I was called"

# used to generate static files for local development.
./manage.py runserver --host=0.0.0.0 --port=5000
