from app.models import MikeRecordProvider
from flask import Flask, request, jsonify
from .auth import AuthProvider


def register_routes(app: Flask, mike_records: MikeRecordProvider,
                    auth: AuthProvider):
    @app.route('/login', method='POST')
    def login():
        if request.is_json():
            data = request.get_json()
            token = data.get('token')
            pwd = token.get('password')
            if token != None:
                if auth.is_logged_in(token):
                    return jsonify({'token': auth.generate_new_token()}), 200
                else:
                    return jsonify({
                        'message':
                        'Your are not logged in. Your token expired or is invalid.'
                    }), 401
            elif pwd != None:
                token = auth.login(pwd)
                if token != None:
                    return jsonify({'token': auth.generate_new_token()}), 200
                else:
                    jsonify({'message': 'Your password was incorrect.'}), 401
            else:
                400
