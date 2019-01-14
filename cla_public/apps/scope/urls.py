# coding: utf-8
from cla_public.apps.scope import scope
from cla_public.apps.scope.views import ScopeDiagnosis, ScopeIneligible, ScopeMediation

view = ScopeDiagnosis.as_view("diagnosis")

scope.add_url_rule("diagnosis/", view_func=view)

scope.add_url_rule("diagnosis/<path:choices>", view_func=view)

scope.add_url_rule("refer/<category_name>", view_func=ScopeIneligible.as_view("ineligible"))

scope.add_url_rule("refer/mediation", view_func=ScopeMediation.as_view("mediation"))
