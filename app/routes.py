from typing import Union
from app.models import MikeRecordProvider
from flask import Flask, Request, request, jsonify, Blueprint
from .auth import AuthProvider
from os import remove
import pymysql
import csv
import pandas as pd
import requests


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

    # Download from MIKE website
    @admin.route('/update', methods=['GET'])
	"""
		Support function utilized elsewhere. Downloads MIKES csv from MIKES google drive
	"""
    def download_from_mikes(itmid, dest):
		def get_confirm_token(respnse):
			for key, value in respnse.cookies.items():
				if key.startswith('download_warning'):
					return value
			return None

		def save_response_content(respnse, dest):
			CHUNK_SIZE = 32768

			with open(dest, "wb") as f:
				for chunk in respnse.iter_content(CHUNK_SIZE):
					if chunk: # filter out keep-alive new chunks
						f.write(chunk)

		URL = "https://drive.google.com/u/0/uc?id=1z-fPcdTbZ97QSGEkwthPvs1KInGeu4j6&export=download"

		session = requests.Session()

		respnse = session.get(URL, params = { 'id' : itmid }, stream = True)
		tkn = get_confirm_token(respnse)

		if tkn:
			params = { 'id' : id, 'confirm' : tkn }
			respnse = session.get(URL, params = params, stream = True)

		save_response_content(respnse, dest)


	"""
		Utilizes download_from_mike to save information from MIKES csv file into local database table.
		Allows country codes to be ignored when necessary - when they are not part of the forest elephant habitat
		-- Assumes an open database connection and an open connection cursor
		-- Assumes everything is run on the LOCAL MACHINE as AN ADMINISTRATOR. if this is incorrect, 
			then the runner of the program will be denied the ability to write and delete the given files from the C drive.
	"""
	def upload_from_mike(conn, conn_cursor):
		# TAKE ID FROM SHAREABLE LINK
		file_id = "1z-fPcdTbZ97QSGEkwthPvs1KInGeu4j6"
		# DESTINATION FILE ON YOUR DISK
		dest = "C:/MIKES.csv"
		download_from_mikes(file_id, dest)

		read_file = pd.read_csv(r'C:/MIKES.csv')
		country_codes = ["ga","cd","cg","cm","cf","ci","lr","gh","td"]

		try:
			with open("C:/MIKES.csv", "r") as MIKE:
				csv_reader = csv.reader(MIKE, delimiter=',')

				for row in csv_reader:
					if row[4] in country_codes:

						un_region = row[0]
						subregion_name = row[1]
						subregion_id = row[2]
						country_name = row[3]
						country_code = row[4]
						mike_site_id = row[5]
						mike_site_name = row[6]
						year = row[7]
						total_number_of_carcasses = row[8]
						number_of_illegal_carcasses = row[9]

						query = "INSERT IGNORE INTO elephantcarcasses VALUES (\"" + un_region + "\", \""\
								"" + subregion_name + "\", \"" + subregion_id + "\", \"" + country_name + "\", \""\
								"" + country_code + "\", \"" + mike_site_id + "\", \"" + mike_site_name + "\", \""\
								"" + year + "\", \"" + total_number_of_carcasses + "\", \""\
								"" + number_of_illegal_carcasses + "\");"

						conn_cursor.execute(query)
						conn.commit()
		# delete file, so it is not saved on machine
		remove("C:/MIKES.csv")
		

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
