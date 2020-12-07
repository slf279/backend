from app.models import MikeRecordProvider
from flask import Flask, request, jsonify, Blueprint
from .auth import AuthProvider


def admin_routes(app: Flask, mike_records: MikeRecordProvider,
                 auth: AuthProvider):
    admin = Blueprint('admin', 'admin', url_prefix='/admin')

    @admin.before_request
    def require_login():
        data = request.get_json()
        if not (data and data.get('token')
                and auth.is_logged_in(data.get('token'))):
            return jsonify({'message': 'You are not logged in'}), 401

    # TODO: Write logic that uploads and edits MIKE records
    @admin.route('/upload', methods=['POST'])
    def upload_records():
        return jsonify({'message': 'Internal server error'}), 500

    @admin.route('/edit', methods=['POST'])
    def edit_records():
        return jsonify({'message': 'Internal server error'}), 500

    app.register_blueprint(admin)


def register_routes(app: Flask, mike_records: MikeRecordProvider,
                    auth: AuthProvider):
    @app.before_request
    def allow_only_json():
        if not request.is_json:
            return jsonify({'message': 'Bad Request'}), 400

    @app.route('/mikerecords', methods=['GET'])
    def fetch_mike_records():
        data = request.get_json()
        # TODO: Filter data based off of JSON values and return the records as JSON objects
        pass

    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        response = jsonify({'message': 'Bad Request'}), 400
        if data is not None:
            token = data.get('token')
            pwd = data.get('password')
            if token is not None:
                if auth.is_logged_in(token):
                    response = jsonify({'token':
                                        auth.generate_new_token()}), 200
                else:
                    response = jsonify({
                        'message':
                        'Your are not logged in. Your token expired or is invalid.'
                    }), 401
            elif pwd != None:
                token = auth.login(pwd)
                if token != None:
                    response = jsonify({'token':
                                        auth.generate_new_token()}), 200
                else:
                    response = jsonify(
                        {'message': 'Your password is incorrect.'}), 401
        return response

    admin_routes(app, mike_records, auth)
