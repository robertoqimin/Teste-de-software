from app.controllers.home_controller import home_blueprint


def register_routes(app):
    app.register_blueprint(home_blueprint)
