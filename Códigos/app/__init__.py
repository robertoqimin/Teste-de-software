from flask import Flask

from config import Config
from .frontend import register_frontend
from .database import init_db
from . import models  # noqa: F401
from .routes import register_routes


def create_app():
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    app.config.from_object(Config)
    init_db()

    register_frontend(app)
    register_routes(app)

    return app
