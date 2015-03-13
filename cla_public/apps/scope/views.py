# -*- coding: utf-8 -*-
import urllib
import requests
from cla_public.libs.views import RequiresSession
from flask import views, render_template, current_app, request


class ScopeDiagnosisApiProxy(RequiresSession, views.MethodView):

    def request_path(self):
        return '{host}{path}/?{params}'.format(
            host=current_app.config['BACKEND_API']['url'],
            path='scope',
            params=urllib.urlencode(request.args))

    def request_args(self):
        return {
            'headers': {
                'Authorization': 'Token {token}'.format(
                    token=current_app.config['ADDRESSFINDER_API_TOKEN'])
            },
            'timeout': current_app.config.get('API_CLIENT_TIMEOUT', None)
        }

    def get(self):
        response = requests.get(self.request_path(), **self.request_args())
        return response.text

    def post(self):
        response = requests.post(self.request_path(), **self.request_args())
        return response.text


class ScopeDiagnosis(RequiresSession, views.MethodView):

    def get(self):
        return render_template('scope/diagnosis.html')



