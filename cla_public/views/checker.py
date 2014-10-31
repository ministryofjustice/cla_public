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

class ProblemForm(Form):
    categories = HelpTextRadioField('What do you need help with?',
                          choices=CATEGORIES,
                          coerce=unicode,
                          validators=[Required()])


class AboutForm(Form):
    pass


class BenefitsForm(Form):
    pass


@checker_blueprint.route('/problem', methods=['GET', 'POST'])
def problem():
    form = ProblemForm()
    if form.validate_on_submit():
        return redirect(url_for('.about'))
    return render_template('problem.html', form=form)


@checker_blueprint.route('/about', methods=['GET', 'POST'])
def about():
    form = AboutForm()
    if form.validate_on_submit():
        return redirect(url_for('.benefits'))
    return render_template('about.html', form=form)


@checker_blueprint.route('/benefits', methods=['GET', 'POST'])
def benefits():
    form = BenefitsForm()
    if form.validate_on_submit():
        return redirect(url_for('.property'))
    return render_template('benefits.html', form=form)

