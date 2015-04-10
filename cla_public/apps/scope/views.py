# -*- coding: utf-8 -*-
import urllib
import requests
from cla_public.apps.checker.api import create_case
from cla_public.libs.views import RequiresSession
from flask import views, render_template, current_app, request, redirect, \
    session, url_for


class ScopeApiMixin(object):

    def request_path(self, path):
        return '{host}{path}?{params}'.format(
            host=current_app.config['BACKEND_API']['url'],
            path=path,
            params=urllib.urlencode(request.args))

    def request_args(self):
        return {
            'timeout': current_app.config.get('API_CLIENT_TIMEOUT', None)
        }

    def get_post_data(self):
        return request.form

    def post_to_scope(self, path='', payload={}):
        path = 'case/%s/diagnosis/%s' % (session['case_ref'], path)
        request_args = self.request_args()
        request_args['json'] = payload#self.get_post_data()
        return requests.post(self.request_path(path), **request_args)


class ScopeDiagnosisApiProxy(RequiresSession, views.MethodView, ScopeApiMixin):
    def post(self, *args, **kwargs):
        return self.post_to_scope().text


class ScopeDiagnosis(RequiresSession, views.MethodView, ScopeApiMixin):

    def create_diagnosis(self):
        create_case()
        response = self.post_to_scope()
        session['diagnosis_ref'] = response.json()['reference']
        return response

    def move_down(self, payload={}):
        return self.post_to_scope('move_down/', payload=payload)

    def get(self, choices='', *args, **kwargs):
        payload = {}

        choices_list = choices.strip('/').split('/')
        if choices_list:
            last_choice = choices_list[-1]
            payload['current_node_id'] = last_choice

        if 'case_ref' not in session or 'diagnosis_ref' not in session:
            self.create_diagnosis()

        response = self.move_down(payload)

        try:
            return render_template('scope/diagnosis.html', response_json=response.json())
        except ValueError:
            return response.text

    def post(self, choices='', *args, **kwargs):
        choices_list = [request.form['choice']]
        if choices:
            choices_list.insert(0, choices.strip('/'))
        next_choices = '/'.join(choices_list)
        return redirect(url_for('.diagnosis-path', choices=next_choices))




