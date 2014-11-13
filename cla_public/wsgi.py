import os

from cla_public.app import create_app


env_name = os.getenv('ENV_NAME', 'FLASK')

app = create_app(config_name=env_name)
