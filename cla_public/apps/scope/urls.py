# -*- coding: utf-8 -*-
from cla_public.apps.scope import scope
from cla_public.apps.scope.views import ScopeDiagnosis

scope.add_url_rule(
    'diagnosis', view_func=ScopeDiagnosis.as_view('diagnosis'))

scope.add_url_rule(
    'api', view_func=ScopeDiagnosis.as_view('diagnosis-api-proxy'))
