# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from flask import Blueprint, render_template

import logging

log = logging.getLogger(__name__)

index_blueprint = Blueprint('index', __name__)


@index_blueprint.route('/')
def index():
    return render_template('index.html')
