# from django.contrib.auth.models import AbstractBaseUser


class ClaUser(object):
    USERNAME_FIELD = 'token'

    def __init__(self, token):
        self.pk = token

    def save(self, *args, **kwargs):
        # TODO call backend api with last_login ?
        pass

    def is_authenticated(self, *args, **kwargs):
        return True
