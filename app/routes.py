from flask import Flask, request, make_response, jsonify, session
from mariadb import ConnectionPool
from .auth import AuthProvider


def register_routes(app: Flask, db: ConnectionPool, auth: AuthProvider):
    @app.route('/', methods=['GET', 'POST'])
    def send_something():
        return 'save elephants'

    @app.route('/login', methods=['GET', 'POST'])
    @auth.require_login()
    def login():
        if request.method == 'GET':
            if auth.is_logged_in():
                return redirect('/admin')
            else:
                return render_template('login.html')
        else:
            if request.form.get('password') and auth.login(
                    request.form.get('password')):
                redirect('/admin')
            else:
                render_template('login.html')
