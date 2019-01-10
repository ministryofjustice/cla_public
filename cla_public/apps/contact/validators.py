# coding: utf-8
from __future__ import unicode_literals
import re

from wtforms.validators import Email, HostnameValidation


class EmailValidator(Email):
    def __init__(self, message=None):
        self.validate_hostname = HostnameValidation(require_tld=True)
        super(Email, self).__init__(r"^[-0-9a-zA-Z.+_\'*+/=?^_`{|}~]+@([^.@][^@]+)$", re.IGNORECASE, message)
