import os
from base64 import b64encode
from typing import Dict, Mapping
from flask import Flask, jsonify, request, make_response, session, redirect
from passlib.hash import argon2
from models import *


def create_app(test_config=None):
    app = Flask(app, instance_relative_config=True)

    if test_config is None:
        # load the instance config from ../instance/config.py
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # create instance folder if it doesn't already exist
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from routes import routes
    app.register_blueprint(routes)


def get_data(
    subregion_id=None,
    country_code=None,
    mikes_site_id=None,
) -> List[MikeRecord]:
    ...


def only_forest_elephants(data) -> Mapping[Dict]:
    # only records in DRC (cd), Congo (cg), Gabon (ga), Cameroon (cm)
    return filter(
        lambda record: record['CountryCode'] in ['cd', 'cg', 'ga', 'cm'], data)


def require_login(action):
    def do_if_logged_in(*args, **kwargs):
        if session.get('logged_in'):
            return action(*args, **kwargs)
        else:
            return redirect('/login')

    return do_if_logged_in
