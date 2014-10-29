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

problem_blueprint = Blueprint('problem', __name__)

# Categories the user needs help with
CATEGORIES = [
    # value, label, inline help text
    ('violence', 'Violence or abuse at home', 'Domestic violence, child abuse, harassment by an ex-partner'),
    ('housing', 'Housing', 'Eviction, homelessness, losing your home, rent arrears'),
    ('debt', 'Debt', 'Money problems, bankruptcy, repossession'),
    ('family', 'Family', 'Divorce, separation, contact with children'),
    ('immigration', 'Immigration and asylum', 'Applying for asylum or permission to stay in the UK'),
    ('benefits', 'Welfare benefits appeals', 'Appealing a decision about your benefits'),
    ('education', 'Education', 'Special educational needs, problems with school places, exclusions, learning difficulties'),
    ('aap', 'Trouble with the police', 'Being treated unfairly by the police, wrongful arrest'),
    ('discrimination', 'Discrimination', 'Being treated unfairly because of your race, sex, sexual orientation'),
    ('consumer', 'Consumer issues', 'Problems when buying goods and services'),
    ('pi', 'Personal injury', 'An accident that was not your fault'),
    ('publiclaw', 'Public law', 'Taking legal action against a public body, like your local council'),
    ('commcare', 'Community care', 'You’re unhappy with the care being provided for yourself or a relative'),
    ('clinneg', 'Clinical negligence', 'Doctors and nurses not treating you with due care'),
    ('mentalhealth', 'Mental health', 'Getting someone to speak for you at a mental health tribunal or inquest'),
    ('crime', 'Crime, criminal law', 'If you’ve been accused of a crime'),
    ('employment', 'Employment', 'Being treated unfairly at work'),
    ('none', 'Any other problem', '')
    ]

class ProblemForm(Form):

    category = HelpTextRadioField('What do you need help with?',
                          choices=CATEGORIES,
                          coerce=unicode,
                          validators=[Required()])


@problem_blueprint.route('/problem', methods=['GET', 'POST'])
def problem():
    form = ProblemForm()
    if form.validate_on_submit():
        redirect(url_for('success'))
    else:
        return render_template('problem.html', form=form)




