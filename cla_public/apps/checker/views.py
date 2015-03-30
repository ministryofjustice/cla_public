# -*- coding: utf-8 -*-
"Checker views"

import os
from flask import abort, render_template, redirect, session, url_for, views, \
    current_app, request
from flask.ext.babel import lazy_gettext as _

from cla_public.apps.checker import checker
from cla_public.apps.checker.api import post_to_eligibility_check_api, \
    get_organisation_list, ApiError
from werkzeug.datastructures import MultiDict
from cla_public.apps.checker.forms import FindLegalAdviserForm
from cla_public.apps.contact.forms import ContactForm
from cla_public.apps.checker.constants import CATEGORIES, \
    ORGANISATION_CATEGORY_MAPPING, NO_CALLBACK_CATEGORIES
from cla_public.apps.checker.forms import AboutYouForm, YourBenefitsForm, \
    ProblemForm, PropertiesForm, SavingsForm, TaxCreditsForm, OutgoingsForm, \
    IncomeForm
from cla_public.libs.utils import override_locale
from cla_public.libs.views import AllowSessionOverride, FormWizard, \
    FormWizardStep, RequiresSession
from cla_public.libs import laalaa


@checker.after_request
def add_header(response):
    """
    Add no-cache headers
    """
    response.headers['Cache-Control'] = 'no-cache, no-store, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response


class UpdatesMeansTest(object):

    def on_valid_submit(self):
        try:
            post_to_eligibility_check_api(self.form)
        except ApiError:
            self.form.errors['timeout'] = _(
                u'There was an error submitting your data. '
                u'Please check and try again.')
            return self.get(step=self.name)
        else:
            return super(UpdatesMeansTest, self).on_valid_submit()


class CheckerStep(UpdatesMeansTest, FormWizardStep):
    pass


class CheckerWizard(AllowSessionOverride, FormWizard):

    steps = [
        ('problem', CheckerStep(ProblemForm, 'problem.html')),
        ('about', CheckerStep(AboutYouForm, 'about.html')),
        ('benefits', CheckerStep(YourBenefitsForm, 'benefits.html')),
        ('property', CheckerStep(PropertiesForm, 'property.html')),
        ('savings', CheckerStep(SavingsForm, 'savings.html')),
        ('benefits-tax-credits', CheckerStep(
            TaxCreditsForm, 'benefits-tax-credits.html')),
        ('income', CheckerStep(IncomeForm, 'income.html')),
        ('outgoings', CheckerStep(OutgoingsForm, 'outgoings.html'))
    ]

    def complete(self):

        if session.needs_face_to_face:
            return redirect(url_for('.face-to-face'))

        if session.ineligible:
            return redirect(url_for(
                '.help_organisations',
                category_name=session.category_slug))

        return redirect(url_for('.eligible'))

    def skip(self, step):

        if session.needs_face_to_face:
            return True

        if step.name not in ('problem', 'about', 'benefits') \
                and session.ineligible:
            return True

        if step.name == 'benefits':
            return not session.is_on_benefits

        if step.name == 'property':
            return not session.owns_property

        if step.name == 'savings':
            return not session.has_savings_or_valuables

        if step.name == 'benefits-tax-credits':
            return not session.children_or_tax_credits

        if session.is_on_passported_benefits:
            return True

        return False


checker.add_url_rule('/<step>', view_func=CheckerWizard.as_view('wizard'))


class FaceToFace(RequiresSession, views.MethodView, object):

    def get(self):
        data = {}

        args = MultiDict(filter(lambda (k, v): v != '', request.args.items()))

        if 'postcode' in args:
            page = 1

            if 'page' in args and args['page'].isdigit():
                page = args['page']
            data = laalaa.find(args['postcode'], page)

        if not session.category:
            session.category_name = 'your issue'

        response = render_template('result/face-to-face.html',
            data=data, form=FindLegalAdviserForm(request.args))
        session.clear()
        return response


checker.add_url_rule(
    '/result/face-to-face', view_func=FaceToFace.as_view('face-to-face'))


class Eligible(RequiresSession, views.MethodView, object):

    def get(self):
        if session.category in NO_CALLBACK_CATEGORIES:
            session.clear()
            data = {}

            args = MultiDict(filter(lambda (k, v): v != '', request.args.items()))

            if 'postcode' in args:
                page = 1
                if 'page' in args and args['page'].isdigit():
                    page = args['page']
                data = laalaa.find(args['postcode'], page)

            return render_template('result/eligible-no-callback.html',
                data=data, form=FindLegalAdviserForm(request.args))

        return render_template('result/eligible.html', form=ContactForm())

checker.add_url_rule(
    '/result/eligible', view_func=Eligible.as_view('eligible'), methods=['GET', 'POST'])


@checker.route('/help-organisations/<category_name>', methods=['GET'])
def help_organisations(category_name):
    if session:
        session.clear()

    category_name = category_name.replace('-', ' ').capitalize()

    # force english as knowledge base languages are in english
    with override_locale('en'):
        requested = lambda (slug, name, desc): name == category_name
        category, name, desc = next(
            iter(filter(requested, CATEGORIES)),
            (None, None, None))

        if category is None:
            abort(404)

        name = unicode(name)

        category_name = ORGANISATION_CATEGORY_MAPPING.get(name, name)
    trans_category_name = ORGANISATION_CATEGORY_MAPPING.get(name, name)

    organisations = get_organisation_list(article_category__name=category_name)
    return render_template(
        'help-organisations.html',
        organisations=organisations,
        category=category,
        category_name=trans_category_name)
