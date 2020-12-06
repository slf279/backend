from datetime import datetime
from typing import Union
from functools import wraps
from flask.json import jsonify
from passlib.hash import argon2
from .models import MasterPasswordProvider
import jwt
import datetime


class AuthProvider():
    def __init__(self, master_pwd_provider: MasterPasswordProvider,
                 secret: str):
        self.master_pwd_provider = master_pwd_provider
        self.secret = secret

    def is_logged_in(self, token: str) -> bool:
        try:
            jwt.decode(token, self.secret)
            return True
        except jwt.ExpiredSignatureError:
            return False

    def login(self, password: str) -> Union[str, None]:
        if argon2.verify(password, self.master_pwd_provider.get_master_pwd()):
            return self.generate_new_token()
        else:
            return None

    def generate_new_token(self):
        return jwt.encode(
            {'exp': datetime.utcnow() + datetime.timedelta(minutes=30)},
            self.secret)

    def require_login(self, action):
        @wraps(action)
        def allow_if_logged_in(*args, **kwargs):
            if self.is_logged_in():
                return action(*args, **kwargs)
            else:
                return jsonify({'message': 'You are not logged in'}), 401

        return allow_if_logged_in
