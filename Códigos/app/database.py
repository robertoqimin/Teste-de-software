import pymysql

from config import Config


def get_connection(use_database=True):
    connection_config = {
        "host": Config.DB_HOST,
        "port": Config.DB_PORT,
        "user": Config.DB_USER,
        "password": Config.DB_PASSWORD,
        "cursorclass": pymysql.cursors.DictCursor,
        "autocommit": True,
    }

    if use_database:
        connection_config["database"] = Config.DB_NAME

    return pymysql.connect(**connection_config)
