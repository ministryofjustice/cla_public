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
            'timeout': current_app.config.get('API_CLIENT_TIMEOUT', None)
        }

    def post(self):
        request_args = self.request_args()
        request_args['data'] = request.form
        response = requests.post(self.request_path(), **request_args)
        return response.text


class ScopeDiagnosis(RequiresSession, views.MethodView):

    def get(self):
        return render_template('scope/diagnosis.html')



