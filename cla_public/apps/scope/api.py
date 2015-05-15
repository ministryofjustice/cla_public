# -*- coding: utf-8 -*-
import urllib
from cla_common.constants import DIAGNOSIS_SCOPE
from django.template.defaultfilters import striptags
import requests
from cla_public.apps.checker.api import post_to_eligibility_check_api
from cla_public.apps.checker.utils import category_option_from_name
from cla_public.libs.utils import override_locale
from flask import current_app, request, session
from flask.ext.babel import gettext


# keys in session
REF_KEY = 'diagnosis_ref'
PREV_KEY = 'diagnosis_previous_choices'


class DiagnosisApiClient(object):

    @property
    def basepath(self):
        path = 'diagnosis/'
        if REF_KEY in session.checker:
            path = '%s%s/' % (path, session.checker[REF_KEY])
        return path

    def request_path(self, path=''):
        path = '%s%s' % (self.basepath,  path)
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

    def create_diagnosis(self):
        if not session.checker.get(REF_KEY):
            response = self.post_to_scope()
            session.checker[REF_KEY] = response.json().get('reference')

    def get_steps_and_direction(self, previous_choices=[], choices_list=[]):
        """
        Returns the steps and direction to traverse the api
        :param previous_choices - choices on last request (saved in session):
        :param choices_list - new choices (from url):
        :return: tuple (steps: list, direction: string)
        """
        diff = len(choices_list) - len(previous_choices)
        if diff < 0:
            direction = 'up'
            steps = list(reversed(previous_choices[diff:]))
        else:
            direction = 'down'
            steps = choices_list[-diff:]
        return (steps, direction)

    def move(self, choices_list=[]):
        """
        This enables a user to jump to parts of the diagnosis and we send a
        request to the api for each step. The api only allows the user to
        move up or down 1 step at a time.

        :param choices_list - new choices (from url):
        :return requests Response object:
        """
        previous_choices = session.checker.get(PREV_KEY, [])
        session.checker[PREV_KEY] = choices_list
        if len(previous_choices) == len(choices_list):
            # reload page - same choices as before
            return requests.get(self.request_path(), **self.request_args())

        steps, direction = self.get_steps_and_direction(
            previous_choices, choices_list)

        for s in steps:
            payload = {
                'current_node_id': s
            }
            resp = self.post_to_scope('move_%s/' % direction, payload=payload)
        return resp

    def get_category(self, response_json):
        category = response_json['category']
        if not category:
            category_name = striptags(response_json['nodes'][0]['label'])
            with override_locale('en'):
                category, name, desc = category_option_from_name(category_name)
        return category

    def save_category(self, category, note=None):
        session.checker['category'] = category
        if category == 'violence':
            category = 'family'
        session.checker.add_note(
            u'User selected category',
            unicode(session.checker.category_name))
        if note:
            session.checker.add_note(
                u'Public Diagnosis note:',
                note)
        post_to_eligibility_check_api(payload={
            'category': category
        })

    def save(self, response_json):
        state = response_json.get('state')
        nodes = response_json.get('nodes', [])
        note = None
        if state == DIAGNOSIS_SCOPE.CONTACT and nodes:
            note = striptags(nodes[-1]['help_text'])

        self.save_category(
            self.get_category(response_json),
            note)

        prev = None
        answers = []
        for node in nodes[:-1]:
            question = gettext('What do you need help with?')
            answer = striptags(node['label'])

            if prev and prev['heading']:
                question = prev['heading']

            answers.append({
                'question': question,
                'answer': answer
            })

            prev = node

        steps = '\n'.join(
            ['%s: %s' % (i['question'], i['answer']) for i in answers]
        )
        steps += '\nOutcome: %s' % state

        session.checker.add_note(
            u'Public Diagnosis nodes',
            steps)

        session.checker['scope_answers'] = answers

diagnosis_api_client = DiagnosisApiClient()
