from app import create_app
from app.data_access import MariaDBRecordProvider, TextFileMasterPasswordProvider
from app.routes import register_routes
from app.auth import AuthProvider

app = create_app()
db = MariaDBRecordProvider(app.config)
pwd_store = TextFileMasterPasswordProvider(app.instance_path)
auth = AuthProvider(pwd_store, app.config['SECRET_KEY'])
register_routes(app, db, db, auth)
