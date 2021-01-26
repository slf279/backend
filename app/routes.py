from typing import Union
from app.models import MikeRecordProvider
from flask import Flask, Request, request, jsonify, Blueprint
from .auth import AuthProvider


def get_auth_token(request: Request) -> Union[str, None]:
    auth_header = request.headers.get('Authorization')
    token = None
    if auth_header:
        try:
            [auth_type, tkn] = auth_header.split(' ')
            if auth_type == "Bearer" and len(tkn) > 0:
                token = tkn
        except ValueError:
            pass
    return token


def admin_routes(app: Flask, mike_records: MikeRecordProvider,
                 auth: AuthProvider):
    admin = Blueprint('admin', 'admin', url_prefix='/admin')

    @admin.before_request
    def require_login():
        auth_failed_response = jsonify({'message':
                                        'You are not logged in'}), 401
        token = get_auth_token(request)
        if token is None or not auth.is_logged_in(token):
            return auth_failed_response

    # TODO: Write logic that uploads and edits MIKE records
    @admin.route('/upload', methods=['POST'])
    def upload_records():
        return jsonify({'message': 'Not implemented yet'}), 500

    # TODO: Download from MIKE website
    @admin.route('/update', methods=['POST'])
    def update_from_mike():
        return jsonify({'message': 'Not implemented yet'}), 500

    @admin.route('/edit', methods=['POST'])
    def edit_records():
        return jsonify({'message': 'Not implemented yet'}), 500

    app.register_blueprint(admin)


def register_routes(app: Flask, mike_records: MikeRecordProvider,
                    auth: AuthProvider):
    @app.before_request
    def filter_request_types():
        if not (request.content_type.startswith('application/json')
                or request.content_type.startswith('multipart/form-data')):
            return jsonify({'message': 'Bad Request'}), 400

    @app.route('/mikerecords', methods=['GET'])
    def fetch_mike_records():
        data = request.get_json()
        # TODO: Filter data based off of JSON values as query parameters and return the records as JSON objects
        pass

    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        pwd = data.get('password') if data is not None else None
        response = jsonify({'message': 'Bad Request'}), 400
        token = get_auth_token(request)
        # if the user wants to refresh their token
        if token:
            if auth.is_logged_in(token):
                response = jsonify({'token': auth.generate_new_token()}), 200
            else:
                response = jsonify({
                    'message':
                    'Your are not logged in. Your token expired or is invalid.'
                }), 401
        # else if user wants to login and get a token
        elif pwd:
            token = auth.login(pwd)
            if token != None:
                response = jsonify({'token': auth.generate_new_token()}), 200
            else:
                response = jsonify({'message':
                                    'Your password is incorrect.'}), 401
        return response

    admin_routes(app, mike_records, auth)
