from flask import request
import urllib2
import ssl
import json
import re

cait_counter = 0
cait_intervention_config = {}

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def get_cait_params(params, category_name, organisations, checker):
    try:
        if category_name != 'Family':
            return params

        if request.path != '/scope/refer/family':
            return params

        try:
            response = urllib2.urlopen('https://raw.githubusercontent.com/ministryofjustice/cla_cait_intervention/master/cla_cait_intervention_config.json', context=ctx)
        except:
            pass
        try:
            cait_intervention_config = json.load(response)
        except:
            print 'Config file was not valid JSON'
            pass

        survey_config = cait_intervention_config.get('survey')
        intervention_config = cait_intervention_config.get('intervention')
        nodes_config = cait_intervention_config.get('nodes')
        links_config = cait_intervention_config.get('links')
        css_config = cait_intervention_config.get('css')

        # Survey
        if survey_config and survey_config.get('run') == True:
            global cait_counter
            params['info_tools'] = True
            survey_urls = survey_config['urls']
            survey_url = survey_urls.get('default')
            try:
                choices = checker['diagnosis_previous_choices']
                entrypoint = nodes_config[choices[1]]
                if entrypoint:
                    entrypoint_url = True
                    nested = entrypoint.get('nested')
                    if nested and choices[2] not in nested:
                        entrypoint_url = False
                    if entrypoint_url:
                        try:
                            survey_url = survey_urls[entrypoint['survey']]
                        except:
                            pass
            except:
                pass
            survey_body = survey_config.get('body')
            survey_body = re.sub(r'##(.*)##', r'<a href="' + survey_url + r'" target="cait_survey">\1</a>', survey_body)
            params['cait_survey'] = {
                'heading': survey_config.get('heading'),
                'body': survey_body
            }
        else:
            params['cait_survey'] = {}

        # CAIT link
        if intervention_config and intervention_config.get('run') == True:
            params['info_tools'] = True
            intervention_quota = intervention_config.get('quota')
            intervention_cycle = intervention_config.get('quota_cycle')
            if intervention_quota and intervention_cycle:
                cait_counter += 1
                cycle_count = cait_counter % intervention_cycle
                if cycle_count < intervention_quota:
                    cycle_count = 0
                variant = 'default' if cycle_count else 'variant-plain'
                params['cait_variant'] = variant
                if variant != 'default':
                    organisations.insert(0, links_config['cait'])
                    for org in organisations:
                        org_class = org['service_name'].replace(' ', '-').lower()
                        org.update({'classname': org_class})

        # Additional CSS injection
        if params['info_tools']:
            params['cait_css'] = css_config

    except:
        pass

    return params