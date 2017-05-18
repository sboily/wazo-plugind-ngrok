# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+


import json
import requests 

from urlparse import urlparse

from flask_menu.classy import register_flaskview
from flask_menu.classy import classy_menu_item

from wazo_admin_ui.helpers.plugin import create_blueprint
from wazo_admin_ui.helpers.classful import BaseView
from wazo_admin_ui.helpers.form import BaseForm

from wtforms.fields import SubmitField, StringField
from wtforms.validators import InputRequired, Length


ngrok = create_blueprint('ngrok', __name__)

class Plugin(object):

    def load(self, dependencies):
        core = dependencies['flask']

        NgrokView.service = NgrokService()
        NgrokView.register(ngrok, route_base='/ngrok')
        register_flaskview(ngrok, NgrokView)

        core.register_blueprint(ngrok)


class NgrokForm(BaseForm):
    port = StringField('Port', [InputRequired(), Length(max=128)])
    protocol = StringField('Protocol', [InputRequired(), Length(max=128)])
    name = StringField('Protocol', [InputRequired(), Length(max=128)])
    submit = SubmitField('Submit')


class NgrokView(BaseView):

    form = NgrokForm
    resource = 'ngrok'

    @classy_menu_item('.ngrok', 'Ngrok', order=11, icon="plane")
    def index(self):
        return super(NgrokView, self).index()


class NgrokService(object):

    def list(self):
        pass

    def get(self, tunnel_id):
        pass

    def update(self, resource):
        pass
