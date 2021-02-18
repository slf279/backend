from typing import Union, Iterable, Optional
from app.models import MikeRecord, MikeRecordProvider, CountryRecordProvider
from flask import Flask, Request, request, jsonify, Blueprint
from .auth import AuthProvider
import requests
import csv
from stringcase import camelcase

MIKE_CSV_ID = "1z-fPcdTbZ97QSGEkwthPvs1KInGeu4j6"
GOOGLE_DRIVE_URL = "https://drive.google.com/u/0/uc"


def has_csv(req: Request, file_field_name: str) -> bool:
    try:
        return req.files[file_field_name].filename.split('.')[-1].lower() == "csv"
    except (KeyError, AttributeError):
        # KeyError in case the file is not in the dictionary
        # AttributeError in case the dictionary returns None
        return False


def parse_mike_csv(csv_lines: Iterable[str]) -> Optional[Iterable[MikeRecord]]:
    reader = csv.DictReader(csv_lines)
    try:
        return [MikeRecord(row["UNRegion"], row["SubregionName"], row["SubregionID"], row["CountryName"],
                           row["CountryCode"], row["MIKEsiteID"], row["MIKEsiteName"],
                           int(row["year"]), int(row["TotalNumberOfCarcasses"]), int(row["NumberOfIllegalCarcasses"]))
                for row in reader]

    except (ValueError, KeyError, csv.Error):
        return None


def obj_to_camel_dict(obj: object) -> dict:
    return {camelcase(key): val for key, val in obj.__dict__.items()}


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


def admin_routes(app: Flask, mike_store: MikeRecordProvider,
                 auth: AuthProvider):
    admin = Blueprint('admin', 'admin', url_prefix='/admin')

    @admin.before_request
    def require_login():
        auth_failed_response = jsonify({'message': 'You are not logged in'}), 401
        token = get_auth_token(request)
        if token is None or not auth.is_logged_in(token):
            return auth_failed_response

    @admin.route('/upload', methods=['POST'])
    def upload_records():
        if not has_csv(request, 'mike_datasheet'):
            return jsonify({'message': 'Requires a CSV file in "mike_datasheet" field.'}), 400
        file = request.files['mike_datasheet']
        try:
            mike_records = parse_mike_csv(map(lambda x: x.decode('utf-8'), file.read().splitlines()))
            if mike_records is None:
                return jsonify({'message': 'The datasheet is in an invalid format'}, 400)
            else:
                mike_store.bulk_update_mike_records(mike_records)
                return jsonify({'message': 'Database has been updated'}), 200
        except UnicodeDecodeError:
            return jsonify({'message': 'Send the CSV file in UTF-8 encoding.'}), 400

    @admin.route('/update', methods=['GET'])
    def update_from_mike():
        res = requests.get(GOOGLE_DRIVE_URL, {"id": MIKE_CSV_ID, "export": "download"})
        mike_records = parse_mike_csv(res.text.splitlines())
        if mike_records is None:
            return jsonify({'message': 'MIKE Records in invalid format. Contact an administrator.'}, 500)
        else:
            mike_store.bulk_update_mike_records(mike_records)
            return jsonify({'message': 'Database has been updated'}), 200

    # TODO: write logic to update database
    @admin.route('/edit', methods=['POST'])
    def edit_records():
        return jsonify({'message': 'Not implemented yet'}), 500

    app.register_blueprint(admin)


def register_routes(app: Flask, mike_store: MikeRecordProvider, country_store: CountryRecordProvider,
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
        mike_records = mike_store.get_all_mike_records()
        dict_records = list(map(obj_to_camel_dict, mike_records))
        return jsonify(dict_records), 200

    @app.route('/countryrecords', methods=['GET'])
    def fetch_country_records():
        country_records = country_store.get_all_country_records()
        dict_records = list(map(obj_to_camel_dict, country_records))
        return jsonify(dict_records), 200

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

    admin_routes(app, mike_store, auth)
