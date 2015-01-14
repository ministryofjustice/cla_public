import os

from cla_public.app import create_app


app = create_app(config_file='config/docker.py')
