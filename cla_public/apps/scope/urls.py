# -*- coding: utf-8 -*-
from cla_public.apps.scope import scope
from cla_public.apps.scope.views import ScopeDiagnosis, ScopeInScope, ScopeIneligible
from flask import render_template

view = ScopeDiagnosis.as_view('diagnosis')

scope.add_url_rule('diagnosis/', view_func=view)

scope.add_url_rule('diagnosis/<path:choices>', view_func=view)

scope.add_url_rule('in-scope/', view_func=ScopeInScope.as_view('in-scope'))

scope.add_url_rule('ineligible/<category_name>', view_func=ScopeIneligible.as_view('ineligible'))


