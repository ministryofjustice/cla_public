#!/bin/bash
cd /home/app/django

python manage.py collectstatic --noinput
