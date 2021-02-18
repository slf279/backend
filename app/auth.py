from datetime import datetime, timedelta
from typing import Union
from .models import MasterPasswordProvider
import jwt
import jwt.exceptions


class AuthProvider:
    def __init__(self, master_pwd_provider: MasterPasswordProvider,
                 secret: str):
        self.master_pwd_provider = master_pwd_provider
        self.secret = secret

    def is_logged_in(self, token: str) -> bool:
        try:
            jwt.decode(token, self.secret)
            return True
        except:
            return False

    def login(self, password: str) -> Union[str, None]:
        if self.master_pwd_provider.verify_pwd(password):
            return self.generate_new_token()
        else:
            return None

    def generate_new_token(self):
        return jwt.encode({
            'exp': datetime.utcnow() + timedelta(minutes=30)
        }, self.secret).decode('utf-8')
