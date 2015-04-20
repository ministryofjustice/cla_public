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
    ORGANISATION_CATEGORY_MAPPING, NO_CALLBACK_CATEGORIES, \
    LAALAA_PROVIDER_CATEGORIES_MAP
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


def handle_find_legal_adviser_form(form, args):
    data = {}
    category = ''
    page = 1

    if 'category' in args:
        category = LAALAA_PROVIDER_CATEGORIES_MAP.get(args['category'])

    if 'postcode' in args:
        if form.validate():
            if 'page' in args and args['page'].isdigit():
                page = args['page']
            data = laalaa.find(args['postcode'], category, page)
            if 'error' in data:
                form.postcode.errors.append(data['error'])
    return data


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
            return redirect(url_for('.face-to-face', category=session.category))

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


class FaceToFace(views.MethodView, object):
    def get(self):
        form = FindLegalAdviserForm(request.args, csrf_enabled=False)
        data = handle_find_legal_adviser_form(form, request.args)

        session.update({ 'ProblemForm': { 'categories': request.args.get('category') }})

        if session.category:
            category_name = session.category_name
        else:
            category_name = 'your issue'

        response = render_template('result/face-to-face.html',
            data=data, form=form, category_name=category_name)

        session.clear()

        return response


checker.add_url_rule(
    '/result/face-to-face', view_func=FaceToFace.as_view('face-to-face'))


class EligibleNoCallBack(views.MethodView, object):
    def get(self):
        form = FindLegalAdviserForm(request.args, csrf_enabled=False)
        data = handle_find_legal_adviser_form(form, request.args)

        session.clear()
        session.update({ 'ProblemForm': { 'categories': request.args.get('category') }})

        return render_template('result/eligible-no-callback.html',
            data=data, form=form, category_name=session.category_name)

checker.add_url_rule(
    '/find-legal-adviser', view_func=EligibleNoCallBack.as_view('find-legal-adviser'))


class Eligible(RequiresSession, views.MethodView, object):

    def get(self):
        if session.category in NO_CALLBACK_CATEGORIES:
            return redirect(url_for('.find-legal-adviser', category=session.category))

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
