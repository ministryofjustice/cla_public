import urllib
import slumber

from django.conf import settings


API_VERSION = 'v1'
BASE_URI = '{base_uri}/checker/api/{version}'.\
    format(base_uri=settings.BACKEND_BASE_URI, version=API_VERSION)

def get_connection(session=None):
    return slumber.API(BASE_URI, session=session)


connection = slumber.API(BASE_URI)



