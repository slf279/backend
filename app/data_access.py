import mariadb
from flask.config import Config


def init_db(config: Config):
    pool = mariadb.connect(host=config['DB_HOST'],
                           port=config['DB_PORT'],
                           user=config['DB_USER'],
                           password=config['DB_PASSWORD'],
                           pool_name="capstone-backend",
                           pool_size=20)
    return pool
