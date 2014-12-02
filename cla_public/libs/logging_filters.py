from flask import current_app


class RequireDebug(object):

    def __init__(self, debug=False):
        self.debug = debug

    def filter(self, record):
        return self.debug == current_app.config['DEBUG']
