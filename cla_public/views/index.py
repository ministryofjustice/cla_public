# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import logging

from flask import Blueprint, render_template, send_from_directory, current_app


log = logging.getLogger(__name__)

base_blueprint = Blueprint('index', __name__)


@base_blueprint.route('/<path:filename>')
def static(filename):
    # HACK: Switch to nginx.
    directory = os.path.join(current_app.static_folder, '../static-templates/')
    return send_from_directory(directory, filename)


@base_blueprint.route('/')
def index():
    return render_template('index.html')


# TODO: static pages created by Clive, Mickey to re-arrange and re-route correctly
@base_blueprint.route('/cookies')
def cookies():
    return render_template('cookies.html')
