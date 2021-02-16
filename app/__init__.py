import os
from typing import Mapping
from flask import Flask


def create_app(test_config: Mapping = None) -> Flask:
    app = Flask(import_name='app', instance_relative_config=True)
    if test_config is None:
        # load the instance config from ../instance/config.json
        try:
            app.config.from_json('config.json')
        except:
            pass
    else:
        app.config.from_mapping(test_config)
    # create instance folder if it doesn't already exist
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app
