#!/usr/bin/env bash
set -e

# used to generate static files for local development.

pip install -r requirements/generated/requirements-dev.txt  && pip install -r requirements/generated/requirements-no-deps.txt --no-deps

BACKEND_BASE_URI=http://localhost:8010 CLA_PUBLIC_CONFIG=config/local.py ./manage.py runserver
