from app import create_app
from app.data_access import init_db
from app.routes import register_routes

app = create_app()
db = init_db(app.config)
register_routes(app, db)
