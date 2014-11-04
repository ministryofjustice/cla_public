# -*- coding: utf-8 -*-
"Checker views"

from flask import abort, render_template, redirect, url_for

import logging

from cla_public.apps.checker import checker
from cla_public.apps.checker.constants import RESULT_OPTIONS
from cla_public.apps.checker.forms import AboutYouForm, YourBenefitsForm, \
    ProblemForm, PropertyForm, SavingsForm, TaxCreditsForm, IncomeAndTaxForm, \
    OutgoingsForm, ApplicationForm


log = logging.getLogger(__name__)


@checker.route('/problem', methods=['GET', 'POST'])
def problem():
    form = ProblemForm()
    if form.validate_on_submit():
        return redirect(url_for('.about'))
    return render_template('problem.html', form=form)


@checker.route('/about', methods=['GET', 'POST'])
def about():
    form = AboutYouForm()
    if form.validate_on_submit():
        return redirect(url_for('.benefits'))
    return render_template('about.html', form=form)


@checker.route('/benefits', methods=['GET', 'POST'])
def benefits():
    form = YourBenefitsForm()
    if form.validate_on_submit():
        return redirect(url_for('.property'))
    return render_template('benefits.html', form=form)


@checker.route('/property', methods=['GET', 'POST'])
def property():
    form = PropertyForm()
    if form.validate_on_submit():
        return redirect(url_for('.savings'))
    return render_template('property.html', form=form)


@checker.route('/savings', methods=['GET', 'POST'])
def savings():
    form = SavingsForm()
    if form.validate_on_submit():
        return redirect(url_for('.benefits_tax_credits'))
    return render_template('savings.html', form=form)


@checker.route('/benefits-tax-credits', methods=['GET', 'POST'])
def benefits_tax_credits():
    form = TaxCreditsForm()
    if form.validate_on_submit():
        return redirect(url_for('.income'))
    return render_template('benefits-tax-credits.html', form=form)


@checker.route('/income', methods=['GET', 'POST'])
def income():
    form = IncomeAndTaxForm()
    if form.validate_on_submit():
        return redirect(url_for('.outgoings'))
    return render_template('income.html', form=form)


@checker.route('/outgoings', methods=['GET', 'POST'])
def outgoings():
    form = OutgoingsForm()
    if form.validate_on_submit():
        return redirect(url_for('.result', outcome='eligible'))
    return render_template('outgoings.html', form=form)


@checker.route('/result/<outcome>', methods=['GET', 'POST'])
def result(outcome):
    "Display the outcome of the means test"

    valid_outcomes = (result for (result, _) in RESULT_OPTIONS)
    if outcome not in valid_outcomes:
        abort(404)

    form = ApplicationForm()
    if form.validate_on_submit():
        return redirect(url_for('.result', outcome='confirmation'))

    return render_template('result/%s.html' % outcome, form=form)
