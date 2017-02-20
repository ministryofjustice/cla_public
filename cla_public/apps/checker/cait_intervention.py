import os
import re

from flask import current_app, request
import requests
from requests.exceptions import ConnectionError, Timeout


def grt_config_url():
    config_branch = 'master'
    if os.environ.get('CLA_ENV') is not 'prod':
        config_branch = 'develop'

    return 'https://raw.githubusercontent.com/ministryofjustice/cla_cait_' \
           'intervention/%s/cla_cait_intervention_config.json' % config_branch


def get_counter(increment=0):
    key = 'cait_counter'
    count = current_app.cache.get(key) or 0
    if increment:
        count += increment
        current_app.cache.set(key, count)
    return count


def get_cait_params(category_name, organisations, choices, truncate=5):
    params = {}
    if category_name != 'Family' or request.path != '/scope/refer/family':
        return params

    try:
        cait_intervention_config = requests.get(
            grt_config_url(), timeout=5, verify=False).json()
    except (ConnectionError, Timeout, ValueError):
        return params

    try:
        # Make sure any errors with the json/config do not effect the site

        survey_config = cait_intervention_config.get('survey', {})
        intervention_config = cait_intervention_config.get('intervention', {})
        nodes_config = cait_intervention_config.get('nodes', {})
        links_config = cait_intervention_config.get('links', {})
        css_config = cait_intervention_config.get('css', '')

        # Survey
        if survey_config.get('run') is True and len(choices) > 2:
            params['info_tools'] = True
            survey_urls = survey_config['urls']
            survey_url = survey_urls.get('default')
            entrypoint = nodes_config.get(choices[1], {})
            survey = entrypoint.get('survey')

            if entrypoint:
                nested = entrypoint.get('nested', [])
                if not nested or choices[2] in nested:
                    survey_url = survey_urls.get(survey, '')

            survey_body = re.sub(
                r'##(.*)##',
                r'<a href="%s" target="cait_survey">\1</a>' % survey_url,
                survey_config.get('body', ''))

            params['cait_survey'] = {
                'heading': survey_config.get('heading'),
                'body': survey_body
            }
        else:
            params['cait_survey'] = {}

        # CAIT link
        if intervention_config.get('run') is True:
            params['info_tools'] = True
            intervention_quota = intervention_config.get('quota')
            intervention_cycle = intervention_config.get('quota_cycle')

            if intervention_quota and intervention_cycle:
                cycle_count = get_counter(increment=1) % intervention_cycle
                if cycle_count < intervention_quota:
                    cycle_count = 0
                variant = 'default' if cycle_count else 'variant-plain'
                params['cait_variant'] = variant
                if variant != 'default':
                    params['truncate'] = truncate + 1
                    print params['truncate']
                    organisations.insert(0, links_config['cait'])
                    for org in organisations:
                        org_class = org['service_name'].replace(' ', '-').lower()
                        org.update({'classname': org_class})

        # Additional CSS injection
        if params.get('info_tools'):
            params['cait_css'] = css_config
    except:
        return {}

    return params
