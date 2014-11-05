# -*- coding: utf-8 -*-
"Base app views"

import os
import logging

from flask import render_template, send_from_directory, current_app

from cla_public.apps.base import base


log = logging.getLogger(__name__)


@base.route('/<path:filename>')
def static(filename):
    # HACK: Switch to nginx.
    directory = os.path.join(current_app.static_folder, '../static-templates/')
    return send_from_directory(directory, filename)


@base.route('/')
def index():
    return render_template('index.html')


@base.route('/cookies')
def cookies():
    return render_template('cookies.html')

@base.route('/privacy')
def privacy():
    return render_template('privacy.html')

@base.route('/feedback')
def feedback():
    return render_template('feedback.html')
