from cla_public.config.testing import *


BACKEND_API = {
    'url': 'http://localhost:{port}/checker/api/v1/'.format(
        port=os.environ.get('CLA_BACKEND_PORT', 8000))
}
