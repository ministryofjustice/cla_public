#!/usr/bin/env bash
set -e

echo "I was called"

# used to generate static files for local development.
BACKEND_BASE_URI=http://localhost:8010 CLA_PUBLIC_CONFIG=config/local.py ./manage.py runserver
