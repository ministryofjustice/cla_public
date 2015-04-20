# -*- coding: utf-8 -*-
from cla_public.apps.scope import scope
from cla_public.apps.scope.views import ScopeDiagnosis
from flask import render_template

view = ScopeDiagnosis.as_view('diagnosis')

def in_scope():
    return render_template('scope/in-scope.html')

scope.add_url_rule('diagnosis/', view_func=view)

scope.add_url_rule('diagnosis/<path:choices>', view_func=view)

scope.add_url_rule('in-scope/', view_func=in_scope)
