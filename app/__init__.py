import os
from typing import Dict, Mapping, List
from flask import Flask, session, redirect


def create_app(test_config: Mapping = None) -> Flask:
    app = Flask(import_name='app', instance_relative_config=True)
    if test_config is None:
        # load the instance config from ../instance/config.json
        app.config.from_json('config.json')
    else:
        app.config.from_mapping(test_config)
    # create instance folder if it doesn't already exist
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app


def only_forest_elephants(data) -> List[Dict]:
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
