# -*- coding: utf-8 -*-
import urllib
from cla_common.constants import DIAGNOSIS_SCOPE
import requests
from cla_public.apps.checker.api import post_to_eligibility_check_api
from cla_public.apps.scope import scope
from cla_public.libs.views import RequiresSession
from flask import views, render_template, current_app, request, session, \
    url_for, redirect


# keys in session
REF_KEY = 'diagnosis_ref'
PREV_KEY = 'diagnosis_previous_choices'

OUTCOME_URLS = {
    DIAGNOSIS_SCOPE.INSCOPE: '/scope/in-scope',
    DIAGNOSIS_SCOPE.OUTOFSCOPE: '/result/face-to-face'
}


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

    def request_path(self, path=''):
        if REF_KEY in session:
            path = 'diagnosis/%s/%s' % (session[REF_KEY], path)
        else:
            path = 'diagnosis/%s' % path
        return '{host}{path}?{params}'.format(
            host=current_app.config['BACKEND_API']['url'],
            path=path,
            params=urllib.urlencode(request.args))

    def request_args(self):
        return {
            'timeout': current_app.config.get('API_CLIENT_TIMEOUT', None)
        }

    def post_to_scope(self, path='', payload={}):
        request_args = self.request_args()
        request_args['json'] = payload
        return requests.post(self.request_path(path), **request_args)


class ScopeDiagnosis(RequiresSession, views.MethodView, ScopeApiMixin):
    response = None

    def create_diagnosis(self):
        response = self.post_to_scope()
        session[REF_KEY] = response.json().get('reference')

    def move(self, payload={}, up=False):
        direction = 'up' if up else 'down'
        return self.post_to_scope('move_%s/' % direction, payload=payload)

    def do_move(self, choices):
        payload = {}
        choices_list = [c for c in choices.strip('/').split('/') if c]
        previous_choices = session.get(PREV_KEY, [])
        session[PREV_KEY] = choices_list
        if choices_list:
            last_choice = choices_list[-1]
            payload['current_node_id'] = last_choice

        prev = len(previous_choices)
        now = len(choices_list)

        if prev == now:
            # reload page - same choices as before
            return requests.get(self.request_path(), **self.request_args())
        else:
            return self.move(
                payload,
                prev > now)

    def save_category(self, category):
        if category == 'violence':
            category = 'family'
        session['category'] = category
        session.add_note(
            u'User selected category:',
            unicode(session.category_name))
        post_to_eligibility_check_api(payload={
            'category': category
        })

    def get(self, choices='', *args, **kwargs):
        if not session.get(REF_KEY):
            self.create_diagnosis()

        response = self.do_move(choices)

        try:
            response_json = response.json()
        except ValueError:
            if current_app.config['DEBUG']:
                return response.text
            raise

        state = response_json.get('state')

        if state and state != DIAGNOSIS_SCOPE.UNKNOWN:
            self.save_category(response_json['category'])

            return redirect(OUTCOME_URLS[state])

        def add_link(choice):
            choices_list = [choice['id']]
            if choices:
                choices_list.insert(0, choices.strip('/'))
            choice['url'] = url_for('.diagnosis',
                                    choices='/'.join(choices_list))
            return choice

        display_choices = map(add_link, response_json.get('choices', []))

        return render_template('scope/diagnosis.html',
                               choices=display_choices,
                               nodes=response_json.get('nodes', []))




