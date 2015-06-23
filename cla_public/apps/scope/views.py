# -*- coding: utf-8 -*-
from cla_common.constants import DIAGNOSIS_SCOPE
from cla_public.apps.checker.views import HelpOrganisations
from cla_public.apps.scope import scope
from cla_public.apps.scope.api import diagnosis_api_client as api
from cla_public.libs.views import RequiresSession
from flask import views, render_template, current_app, url_for, \
    redirect, session


OUTCOME_URLS = {
    DIAGNOSIS_SCOPE.INSCOPE:    ('wizard', {'step': 'about'}),
    DIAGNOSIS_SCOPE.INELIGIBLE: ('scope.ineligible', None),
    DIAGNOSIS_SCOPE.OUTOFSCOPE: ('scope.ineligible', {'category_name': 'legal-adviser'}),
    DIAGNOSIS_SCOPE.MEDIATION:  ('scope.ineligible', {'category_name': 'mediation'}),
    DIAGNOSIS_SCOPE.CONTACT:    ('contact.get_in_touch', {}),
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


class ScopeDiagnosis(RequiresSession, views.MethodView):
    def get(self, choices='', *args, **kwargs):
        api.create_diagnosis()

        response = api.move([c for c in choices.strip('/').split('/') if c])

        try:
            response_json = response.json()
        except ValueError:
            if current_app.config['DEBUG']:
                return response.text
            raise

        state = response_json.get('state')
        nodes = response_json.get('nodes', [])

        if state and state != DIAGNOSIS_SCOPE.UNKNOWN:
            api.save(response_json)

            outcome_url = OUTCOME_URLS[state]
            if state == DIAGNOSIS_SCOPE.INELIGIBLE:
                outcome_url = url_for(outcome_url[0],
                                      category_name=session.checker.category_slug)
            else:
                outcome_url = url_for(outcome_url[0], **outcome_url[1])
                if state == DIAGNOSIS_SCOPE.OUTOFSCOPE:
                    outcome_url = '%s?category=%s' % (
                        outcome_url,
                        session.checker.category)
            return redirect(outcome_url)

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


class ScopeIneligible(HelpOrganisations):
    _template = 'scope/ineligible.html'


class ScopeMediation(RequiresSession, views.MethodView):
    def get(self):
        return render_template('scope/mediation.html')
