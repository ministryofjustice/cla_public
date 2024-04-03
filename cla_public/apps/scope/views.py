# coding: utf-8
from cla_common.constants import DIAGNOSIS_SCOPE
from cla_public.apps.base.utils import check_categories
from cla_public.apps.checker.views import HelpOrganisations
from cla_public.apps.scope import scope
from cla_public.apps.scope.api import diagnosis_api_client as api
from cla_public.libs.views import RequiresSession
from flask import views, render_template, current_app, url_for, redirect, session


OUTCOME_URLS = {
    DIAGNOSIS_SCOPE.INSCOPE: ("checker.interstitial", {}, None),
    DIAGNOSIS_SCOPE.INELIGIBLE: ("scope.ineligible", None, "referred/help-organisations/scope"),
    DIAGNOSIS_SCOPE.OUTOFSCOPE: ("scope.ineligible", {"category_name": "legal-adviser"}, "referred/f2f/scope"),
    DIAGNOSIS_SCOPE.MEDIATION: ("scope.ineligible", {"category_name": "mediation"}, "referred/mediation/scope"),
    DIAGNOSIS_SCOPE.CONTACT: ("contact.get_in_touch", {}, "incomplete"),
}


@scope.after_request
def add_header(response):
    """
    Add no-cache headers
    """
    response.headers["Cache-Control"] = "no-cache, must-revalidate, no-store, max-age=0"
    response.headers["Pragma"] = "no-cache"
    return response


class ScopeDiagnosis(RequiresSession, views.MethodView):
    # flake8: noqa: C901
    def get(self, choices="", *args, **kwargs):
        api.create_diagnosis()

        response = api.move([c for c in choices.strip("/").split("/") if c])

        try:
            response_json = response.json()
        except ValueError:
            if current_app.config["DEBUG"]:
                return response.text
            raise

        state = response_json.get("state")
        nodes = response_json.get("nodes", [])

        if state and state != DIAGNOSIS_SCOPE.UNKNOWN:
            api.save(response_json)

            outcome_url = OUTCOME_URLS[state]
            outcome = outcome_url[2]

            if outcome:
                session.store({"outcome": outcome})

            if state == DIAGNOSIS_SCOPE.INELIGIBLE:
                outcome_url = url_for(outcome_url[0], category_name=session.checker.category_slug)
            else:
                try:
                    is_hlpas = "yes" if nodes[-2]["context"]["hlpas"].lower() == "true" else "no"
                except Exception:
                    is_hlpas = "no"

                outcome_url[1]["hlpas"] = is_hlpas

                if state == DIAGNOSIS_SCOPE.OUTOFSCOPE:
                    category = self.get_category_for_larp(session)
                    outcome_url[1]["category"] = category

                outcome_url = url_for(outcome_url[0], **outcome_url[1])

            return redirect(outcome_url)

        def add_link(choice):
            choices_list = [choice["id"]]
            if choices:
                choices_list.insert(0, choices.strip("/"))
            choice["url"] = url_for(".diagnosis", choices="/".join(choices_list))
            return choice

        display_choices = map(add_link, response_json.get("choices", []))

        return render_template("scope/diagnosis.html", choices=display_choices, nodes=nodes)

    def get_category_for_larp(self, session):
        categories_list = ["n88", "n149"]
        if check_categories(session, categories_list):
            return "traffickingandslavery"
        return session.checker.category


class ScopeIneligible(HelpOrganisations):
    _template = "scope/ineligible.html"


class ScopeMediation(views.MethodView):
    def get(self):
        session.clear_checker()
        return render_template("scope/mediation.html")
