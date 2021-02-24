from typing import Iterable, Optional
from app.models import MikeRecord, MikeRecordProvider, CountryRecordProvider, InvalidRecordError, \
    InvalidPrimaryKeyOperationError
from flask import Flask, Request, request, jsonify, Blueprint
from .auth import AuthProvider
import requests
import csv
from stringcase import camelcase

MIKE_CSV_ID = '1z-fPcdTbZ97QSGEkwthPvs1KInGeu4j6'
GOOGLE_DRIVE_URL = 'https://drive.google.com/u/0/uc'
VALID_COUNTRY_CODES = {'ga', 'cd', 'cg', 'cm', 'cf', 'ci', 'lr', 'gh', 'td'}


def has_csv(req: Request, file_field_name: str) -> bool:
    try:
        return req.files[file_field_name].filename.split('.')[-1].lower() == 'csv'
    except (KeyError, AttributeError):
        # KeyError in case the file is not in the dictionary
        # AttributeError in case the dictionary returns None
        return False


def parse_mike_csv(csv_lines: Iterable[str]) -> Optional[Iterable[MikeRecord]]:
    reader = csv.DictReader(csv_lines)
    try:
        return [MikeRecord(row['UNRegion'], row['SubregionName'], row['SubregionID'], row['CountryName'],
                           row['CountryCode'], row['MIKEsiteID'], row['MIKEsiteName'],
                           int(row['year']), int(row['TotalNumberOfCarcasses']), int(row['NumberOfIllegalCarcasses']))
                for row in reader]

    except (ValueError, KeyError, csv.Error, InvalidRecordError):
        return None


def obj_to_camel_dict(obj: object) -> dict:
    return {camelcase(key): val for key, val in obj.__dict__.items()}


def json_dict_to_mike(json_dict: dict) -> MikeRecord:
    return MikeRecord(json_dict['unRegion'], json_dict['subregionName'], json_dict['subregionId'],
                      json_dict['countryName'], json_dict['countryCode'], json_dict['mikeSiteId'],
                      json_dict['mikeSiteName'], json_dict['year'], json_dict['carcasses'],
                      json_dict['illegalCarcasses'])


def get_auth_token(req: Request) -> Optional[str]:
    auth_header = req.headers.get('Authorization')
    token = None
    if auth_header:
        try:
            [auth_type, tkn] = auth_header.split(' ')
            if auth_type == 'Bearer' and len(tkn) > 0:
                token = tkn
        except ValueError:
            pass
    return token


def register_admin_routes(app: Flask, mike_store: MikeRecordProvider,
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
                return jsonify({'message': 'The datasheet is in an invalid format.'}, 400)
            else:
                mike_store.add_or_overwrite_mike_records(
                    [x for x in mike_records if x.country_code in VALID_COUNTRY_CODES])
                return jsonify({'message': 'Database has been updated.'}), 200
        except UnicodeDecodeError:
            return jsonify({'message': 'Send the CSV file in UTF-8 encoding.'}), 400

    @admin.route('/update', methods=['GET'])
    def update_from_mike():
        res = requests.get(GOOGLE_DRIVE_URL, {'id': MIKE_CSV_ID, 'export': 'download'})
        mike_records = parse_mike_csv(res.text.splitlines())
        if mike_records is None:
            return jsonify({'message': 'MIKE Records in invalid format. Contact an administrator.'}), 500
        else:
            mike_store.add_or_overwrite_mike_records(
                [x for x in mike_records if x.country_code in VALID_COUNTRY_CODES])
            return jsonify({'message': 'Database has been updated'}), 200

    @admin.route('/edit', methods=['POST'])
    def edit_records():
        data = request.get_json()
        res = jsonify({'message': 'Bad Request'}), 400
        if data is not None:
            try:
                records_to_add = [json_dict_to_mike(x) for x in data.get('added', [])]
                mike_store.add_mike_records(records_to_add)
                records_to_change = [json_dict_to_mike(x) for x in data.get('changed', [])]
                mike_store.update_mike_records(records_to_change)
                records_to_remove = [MikeRecord.PrimaryKey(x['mikeSiteId'], x['year']) for x in data.get('removed', [])]
                mike_store.remove_mike_records(records_to_remove)
                return jsonify({'message': 'Database has been updated.'}), 200
            except (ValueError, KeyError, InvalidRecordError):
                return jsonify({'message': 'One or more of the records supplied are invalid.'}), 400
            except InvalidPrimaryKeyOperationError as e:
                return jsonify({'message': 'Attempted to add a record whose primary key is already in the database.',
                               'problemRecord': obj_to_camel_dict(e.record)}), 400
        return res

    app.register_blueprint(admin)


def register_routes(app: Flask, mike_store: MikeRecordProvider, country_store: CountryRecordProvider,
                    auth: AuthProvider):
    @app.before_request
    def filter_request_types():
        if (request.method == 'POST'
                and not (request.content_type is not None
                         or request.content_type.startswith(
                            'application/json')
                         or request.content_type.startswith(
                            'multipart/form-data'))):
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
        token = get_auth_token(request)
        # if the user wants to refresh their token
        if token:
            if auth.is_logged_in(token):
                return jsonify({'token': auth.generate_new_token()}), 200
            # else check password
        # else if user wants to login and get a token
        if pwd:
            token = auth.login(pwd)
            if token is not None:
                return jsonify({'token': auth.generate_new_token()}), 200
            else:
                return jsonify({'message': 'Your password is incorrect.'}), 401
        return jsonify({'message': 'Bad Request'}), 400

    register_admin_routes(app, mike_store, auth)
