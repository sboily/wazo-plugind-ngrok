# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+


import json
import requests 
import yaml

from flask_classful import route
from flask import request
from flask import render_template

from flask_menu.classy import register_flaskview
from flask_menu.classy import classy_menu_item

from wazo_admin_ui.helpers.plugin import create_blueprint
from wazo_admin_ui.helpers.classful import BaseView
from wazo_admin_ui.helpers.form import BaseForm

from wtforms.fields import SubmitField, StringField, SelectField, BooleanField
from wtforms.validators import InputRequired, Length


ngrok = create_blueprint('ngrok', __name__)
ngrok_config = '/etc/ngrok/ngrok.yml'

class Plugin(object):

    def load(self, dependencies):
        core = dependencies['flask']

        NgrokView.service = NgrokService()
        NgrokView.register(ngrok, route_base='/ngrok')
        register_flaskview(ngrok, NgrokView)

        core.register_blueprint(ngrok)


class NgrokForm(BaseForm):
    port = StringField('Port', [InputRequired(), Length(max=128)])
    protocol = SelectField('Protocol', choices=[('tcp', 'TCP'), ('http', 'HTTP'), ('tls', 'TLS')])
    name = StringField('Name', [InputRequired(), Length(max=128)])
    subdomain = StringField('Subdomain', [Length(max=128)])
    auth = StringField('Auth', [Length(max=128)])
    bind_tls = SelectField('Bind TLS', choices=[('true', 'True'), ('false', 'False'), ('both', 'Both')])
    use_wazo_crt = BooleanField('Use Wazo certificates')
    submit = SubmitField('Submit')

class NgrokConfigForm(BaseForm):
    authtoken = StringField('Auth Token',
                            [InputRequired(), Length(max=128)],
                            render_kw={'type': 'password',
                                       'data_toggle': 'password'})
    region = SelectField('Region', choices=[('us', 'United States'), ('eu', 'Europe'), ('ap', 'Asia/Pacific'), ('au', 'Australia')])
    submit = SubmitField('Submit')


class NgrokView(BaseView):

    form = NgrokForm
    resource = 'ngrok'

    @classy_menu_item('.ngrok', 'Ngrok', order=11, icon="plane")
    @classy_menu_item('.ngrok.tunnels', 'Tunnels', order=2, icon="lock")
    def index(self):
        return super(NgrokView, self).index()

    @route('/auth_token', methods=['POST'])
    def auth_token(self):
        self.service.update_config(request.form)
        return self.config()

    @classy_menu_item('.ngrok.config', 'Configuration', order=1, icon="gear")
    def config(self):
        resource = self.service.get_resource()
        form = NgrokConfigForm(data=resource)
        return render_template('ngrok/config.html', form=form, resource=resource)


class NgrokService(object):

    base_url = 'http://localhost:4040/api/tunnels'
    headers = {'content-type': 'application/json'}

    def list(self):
        r = requests.get(self.base_url)
        if r.status_code == 200:
            return r.json()

    def create(self, resources):
        tunnel = {
            'addr': resources.get('port'),
            'proto': resources.get('protocol'),
            'name': resources.get('name')
        }

        if resources.get('auth') and resources.get('protocol') == 'http':
            tunnel['auth'] = resources.get('auth')
        if resources.get('subdomain'):
            tunnel['subdomain'] = resources.get('subdomain')
        if resources.get('bind_tls') and resources.get('protocol') == 'http':
            tunnel['bind_tls'] = resources.get('bind_tls')

        if resources.get('use_wazo_crt') and resources.get('protocol') == 'tls':
            tunnel['crt'] = '/usr/share/xivo-certs/server.crt'
            tunnel['key'] = '/usr/share/xivo-certs/server.key'

        r = requests.post(self.base_url, data=json.dumps(tunnel), headers=self.headers)
        if r.status_code == 201:
            return r.json()

    def update_config(self, form):
        if self._update_yml(form):
            self._restart_ngrok()

    def delete(self, name):
        url = '{}/{}'.format(self.base_url, name)
        requests.delete(url, headers=self.headers)

    def get_resource(self):
        with open(ngrok_config, 'r') as stream:
            try:
                return yaml.load(stream)
            except yaml.YAMLError as e:
                print(e)

        return {}

    def _update_yml(self, form):
        data = {
            'authtoken': '{}'.format(form.get('authtoken')),
            'region': '{}'.format(form.get('region'))
        }
        with open(ngrok_config, 'w') as stream:
            yaml.dump(data, stream, default_flow_style=False)
            return True

        return False

    def _restart_ngrok(self):
        uri = 'http://localhost:8668/services'
        headers = {'content-type': 'application/json'}
        service = {'ngrok': 'restart'}
        req = requests.post(uri, data=json.dumps(service), headers=headers)
