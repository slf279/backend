from typing import Union, List
from app.models import MikeRecord, MikeRecordProvider
from flask import Flask, Request, request, jsonify, Blueprint
from .auth import AuthProvider
import requests
import csv

MIKE_CSV_ID = "1z-fPcdTbZ97QSGEkwthPvs1KInGeu4j6"
GOOGLE_DRIVE_URL = "https://drive.google.com/u/0/uc"


def get_auth_token(req: Request) -> Union[str, None]:
    auth_header = req.headers.get('Authorization')
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
        auth_failed_response = jsonify({'message': 'You are not logged in'}), 401
        token = get_auth_token(request)
        if token is None or not auth.is_logged_in(token):
            return auth_failed_response

    # TODO: Write logic that uploads and edits MIKE records
    @admin.route('/upload', methods=['POST'])
    def upload_records():
        return jsonify({'message': 'Not implemented yet'}), 500

    @admin.route('/update', methods=['GET'])
    def update_from_mike():

        res = requests.get(GOOGLE_DRIVE_URL, {"id": MIKE_CSV_ID, "export": "download"})
        mike_data = csv.reader(res.text.splitlines())
        mike_data.next()  # skip header lines

        def mike_record_from_list(list_record: List[str]):
            tuple_record = tuple(list_record[0:7]) + (int(list_record[7]), int(list_record[8]), int(list_record[9]))
            return MikeRecord.from_tuple(tuple_record)

        try:
            mike_records.bulk_update_mike_records(map(mike_record_from_list, mike_data))
            return jsonify({'message': 'Database has been updated'}), 200
        except (ValueError, IndexError):
            return jsonify({'message': 'MIKE Records in invalid format. Contact an administrator.'}, 500)

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

    @app.errorhandler(404)
    def report_not_found(_):
        return jsonify({'message': 'Not Found'}), 404

    @app.errorhandler(500)
    def report_internal_error(_):
        return jsonify({'message': 'Internal Server Error'}), 500

    @app.route('/mikerecords', methods=['GET'])
    def fetch_mike_records():
        mike_records.get_all_mike_records()
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
            if token is not None:
                response = jsonify({'token': auth.generate_new_token()}), 200
            else:
                response = jsonify({'message': 'Your password is incorrect.'}), 401
        return response

    admin_routes(app, mike_records, auth)
