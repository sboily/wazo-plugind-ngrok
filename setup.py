#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from setuptools import find_packages
from setuptools import setup

setup(
    name='wazo_admin_ui_ngrok',
    version='0.1',

    description='Wazo Admin UI ngrok',

    author='Sylvain Boily',
    author_email='sboily@wazo.community',

    url='http://ngrok.com',

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    package_data={
        'wazo_plugind_admin_ui_ngrok_official': ['templates/*/*.html'],
    },

    entry_points={
        'wazo_admin_ui.plugins': [
            'ngrok = wazo_plugind_admin_ui_ngrok_official.plugin:Plugin',
        ]
    }
)
