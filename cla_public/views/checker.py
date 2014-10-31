# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from flask import Blueprint, render_template, redirect, url_for
from wtforms import (TextField, HiddenField, RadioField, PasswordField,
                     BooleanField, SubmitField, validators)
from wtforms.validators import Required
from flask_wtf import Form

import logging

from cla_public.views.custom import HelpTextRadioField

log = logging.getLogger(__name__)

checker_blueprint = Blueprint('checker', __name__)
result_blueprint = Blueprint('result', __name__)

# Categories the user needs help with
CATEGORIES = [
    # value, label, inline help text
    ('clinneg', 'Clinical negligence', 'Doctors and nurses not treating you with due care'),
    ('commcare', 'Community care', 'You’re unhappy with the care being provided for yourself or a relative'),
    ('debt', 'Debt', 'Money problems, bankruptcy, repossession'),
    ('discrimination', 'Discrimination', 'Being treated unfairly because of your race, sex, sexual orientation'),
    ('education', 'Education', 'Special educational needs, problems with school places, exclusions, learning difficulties'),
    ('family', 'Family', 'Divorce, separation, contact with children'),
    ('housing', 'Housing', 'Eviction, homelessness, losing your home, rent arrears'),
    ('immigration', 'Immigration and asylum', 'Applying for asylum or permission to stay in the UK'),
    ('mentalhealth', 'Mental health', 'Getting someone to speak for you at a mental health tribunal or inquest'),
    ('pi', 'Personal injury', 'An accident that was not your fault'),
    ('publiclaw', 'Public law', 'Taking legal action against a public body, like your local council'),
    ('aap', 'Trouble with the police', 'Being treated unfairly by the police, wrongful arrest'),
    ('violence', 'Violence or abuse at home', 'Domestic violence, child abuse, harassment by an ex-partner'),
    ('benefits', 'Welfare benefits appeals', 'Appealing a decision about your benefits')
]

RESULT_OPTIONS = [
    ('eligible', 'Eligible'),
    ('ineligible', 'Ineligible'),
    ('face-to-face', 'Face-to-face'),
    ('confirmation', 'Confirmation'),
]

class ProblemForm(Form):
    categories = HelpTextRadioField('What do you need help with?',
                          choices=CATEGORIES,
                          coerce=unicode,
                          validators=[Required()])


class ProceedForm(Form):
    proceed = BooleanField(validators=[Required('Not a valid choice')])

class ResultForm(Form):
    result = RadioField(choices=RESULT_OPTIONS, validators=[Required('Not a valid choice')])


@checker_blueprint.route('/problem', methods=['GET', 'POST'])
def problem():
    form = ProblemForm()
    if form.validate_on_submit():
        return redirect(url_for('.about'))
    return render_template('problem.html', form=form)


@checker_blueprint.route('/about', methods=['GET', 'POST'])
def about():
    form = ProceedForm()
    if form.validate_on_submit():
        return redirect(url_for('.benefits'))
    return render_template('about.html', form=form)


@checker_blueprint.route('/benefits', methods=['GET', 'POST'])
def benefits():
    form = ProceedForm()
    if form.validate_on_submit():
        return redirect(url_for('.property'))
    return render_template('benefits.html', form=form)


@checker_blueprint.route('/property', methods=['GET', 'POST'])
def property():
    form = ProceedForm()
    if form.validate_on_submit():
        return redirect(url_for('.savings'))
    return render_template('property.html', form=form)


@checker_blueprint.route('/savings', methods=['GET', 'POST'])
def savings():
    form = ProceedForm()
    if form.validate_on_submit():
        return redirect(url_for('.benefits_tax_credits'))
    return render_template('savings.html', form=form)


@checker_blueprint.route('/benefits-tax-credits', methods=['GET', 'POST'])
def benefits_tax_credits():
    form = ProceedForm()
    if form.validate_on_submit():
        return redirect(url_for('.income'))
    return render_template('benefits-tax-credits.html', form=form)


@checker_blueprint.route('/income', methods=['GET', 'POST'])
def income():
    form = ProceedForm()
    if form.validate_on_submit():
        return redirect(url_for('.outgoings'))
    return render_template('income.html', form=form)


@checker_blueprint.route('/outgoings', methods=['GET', 'POST'])
def outgoings():
    form = ResultForm()
    if form.validate_on_submit():
        return redirect(url_for('result.show', outcome=form.data['result']))
    return render_template('outgoings.html', form=form)


@result_blueprint.route('/result/<outcome>', methods=['GET', 'POST'])
def show(outcome):
    try:
        return render_template('result/%s.html' % outcome)
    except TemplateNotFound:
        abort(404)
