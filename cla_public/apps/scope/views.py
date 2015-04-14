# -*- coding: utf-8 -*-
import urllib
from cla_common.constants import DIAGNOSIS_SCOPE
import requests
from cla_public.apps.checker.api import create_case, \
    post_to_eligibility_check_api
from cla_public.apps.scope import scope
from cla_public.libs.views import RequiresSession
from flask import views, render_template, current_app, request, session, \
    url_for, redirect


@scope.after_request
def add_header(response):
    """
    Add no-cache headers
    """
    response.headers['Cache-Control'] = \
        'no-cache, must-revalidate, no-store, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response


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

    def post_to_scope(self, path='', payload={}):
        if 'diagnosis_ref' in session:
            path = 'diagnosis/%s/%s' % (session['diagnosis_ref'], path)
        else:
            path = 'diagnosis/%s' % path
        request_args = self.request_args()
        request_args['json'] = payload
        return requests.post(self.request_path(path), **request_args)


class ScopeDiagnosis(RequiresSession, views.MethodView, ScopeApiMixin):

    def create_diagnosis(self):
        response = self.post_to_scope()
        session['diagnosis_ref'] = response.json()['reference']
        return response

    def move(self, payload={}, up=False):
        direction = 'up' if up else 'down'
        return self.post_to_scope('move_%s/' % direction, payload=payload)

    def get(self, choices='', *args, **kwargs):
        payload = {}

        choices_list = choices.strip('/').split('/')
        previous_choices = session.get('diagnosis_previous_choices', [])
        session['diagnosis_previous_choices'] = choices_list
        if choices_list:
            last_choice = choices_list[-1]
            payload['current_node_id'] = last_choice

        if 'diagnosis_ref' not in session:
            self.create_diagnosis()

        response = self.move(
            payload,
            len(previous_choices) > len(choices_list))

        # Temporary for debugging
        try:
            response_json = response.json()
        except ValueError:
            return response.text

        if response_json['state'] != DIAGNOSIS_SCOPE.UNKNOWN:
            category = response_json['category']
            if category == 'violence':
                category = 'family'
            session['ProblemForm'] = session.get('AboutYouForm', {})
            session['ProblemForm']['categories'] = category
            session.add_note(u'User selected category: {0}'.format(category))
            payload = {
                'category': category
            }
            post_to_eligibility_check_api(payload=payload)

            if response_json['state'] == DIAGNOSIS_SCOPE.INSCOPE:
                return redirect('/about')
            elif response_json['state'] == DIAGNOSIS_SCOPE.OUTOFSCOPE:
                return redirect('/result/face-to-face')

        def add_link(choice):
            choices_list = [choice['id']]
            if choices:
                choices_list.insert(0, choices.strip('/'))
            choice['url'] = url_for('.diagnosis',
                                    choices='/'.join(choices_list))
            return choice

        display_choices = map(add_link, response_json.get('choices', []))

        return render_template('scope/diagnosis.html',
                               choices=display_choices)




