import slumber

from django.conf import settings

from api.client import get_auth_connection

from .models import ClaUser



class ClaBackend(object):
    """
    """
    def authenticate(self, username=None, password=None):

        connection = get_auth_connection()

        response = connection.oauth2.access_token.post({
            'client_id': settings.AUTH_CLIENT_ID,
            'client_secret': settings.AUTH_CLIENT_SECRET,
            'grant_type': 'password',
            'username': username,
            'password': password
        })

        user = ClaUser(response['access_token'])
        return user

    def get_user(self, token):
        return ClaUser(token)
