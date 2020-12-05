from functools import wraps
from flask import session
from passlib.hash import argon2


class AuthProvider():
    def __init__(self):
        pass

    def is_logged_in() -> bool:
        return bool(session.get('logged_in'))

    def login(password: str) -> bool:
        # TODO: store master password hash in database and fetch it here
        master_pwd_hash = argon2.hash('save the elephants')
        if argon2.verify(password, master_pwd_hash):
            session.set('logged_in', True)
        else:
            session.set('logged_in', False)
        return session.get('logged_in')

    def logout():
        session.set('logged_in', False)

    def require_login(action):
        @wraps(action)
        def allow_if_logged_in(*args, **kwargs):
            if is_logged_in():
                return action(*args, **kwargs)
            else:
                return redirect('/login')

        return allow_if_logged_in
