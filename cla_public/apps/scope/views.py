# -*- coding: utf-8 -*-
import urllib
from cla_common.constants import DIAGNOSIS_SCOPE
from django.template.defaultfilters import striptags
import requests
from cla_public.apps.checker.api import post_to_eligibility_check_api
from cla_public.apps.checker.utils import category_option_from_name
from cla_public.apps.scope import scope
from cla_public.libs.utils import override_locale
from cla_public.libs.views import RequiresSession
from flask import views, render_template, current_app, request, session, \
    url_for, redirect


# keys in session
REF_KEY = 'diagnosis_ref'
PREV_KEY = 'diagnosis_previous_choices'

OUTCOME_URLS = {
    DIAGNOSIS_SCOPE.INSCOPE: '/scope/in-scope',
    DIAGNOSIS_SCOPE.OUTOFSCOPE: '/result/face-to-face',
    DIAGNOSIS_SCOPE.CONTACT: '/contact',
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

    def move(self, previous_choices=[], choices_list=[]):
        """
        This enables a user to jump to parts of the diagnosis and we send a
        request to the api for each step. The api only allows the user to
        move up or down 1 step at a time.

        :param previous_choices - choices on last request (saved in session):
        :param choices_list - new choices (from url):
        :return requests Response object:
        """
        prev = len(previous_choices)
        now = len(choices_list)
        diff = now - prev
        if prev == now:
            # reload page - same choices as before
            return requests.get(self.request_path(), **self.request_args())
        elif prev > now:
            direction = 'up'
            steps = reversed(previous_choices[diff:])
        else:
            direction = 'down'
            steps = choices_list[-diff:]

        for s in steps:
            payload = {}
            payload['current_node_id'] = s
            resp = self.post_to_scope('move_%s/' % direction, payload=payload)
        return resp

    def do_move(self, choices):
        choices_list = [c for c in choices.strip('/').split('/') if c]
        previous_choices = session.get(PREV_KEY, [])
        session[PREV_KEY] = choices_list

        return self.move(
                previous_choices,
                choices_list)

    def get_category(self, response_json):
        category = response_json['category']
        if not category:
            category_name = striptags(response_json['nodes'][0]['label'])
            with override_locale('en'):
                category, name, desc = category_option_from_name(category_name)
        return category

    def save_category(self, category, note=None):
        session['category'] = category
        if category == 'violence':
            category = 'family'
        session.add_note(
            u'User selected category:',
            unicode(session.category_name))
        if note:
            session.add_note(
                u'Public Diagnosis note:',
                note)
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
        nodes = response_json.get('nodes', [])

        if state and state != DIAGNOSIS_SCOPE.UNKNOWN:
            note = None
            if state == DIAGNOSIS_SCOPE.CONTACT and nodes:
                note = striptags(nodes[-1]['help_text'])
            self.save_category(self.get_category(response_json), note)

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
                               nodes=nodes)


class ScopeInScope(views.MethodView):
    def get(self, *args, **kwargs):
        return render_template('scope/in-scope.html')




