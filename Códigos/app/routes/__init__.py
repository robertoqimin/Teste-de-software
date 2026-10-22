from app.routes.api_routes import api_bp, register_api_errors
from app.routes.document_routes import document_bp
from app.routes.home_routes import home_blueprint
from app.routes.auth_routes import auth_bp
from app.routes.professor_routes import professor_bp
from app.routes.aluno_routes import aluno_bp


def register_routes(app):
    from app.routes.gestao_routes import gestao_bp
    app.register_blueprint(gestao_bp)
    app.register_blueprint(api_bp)
    register_api_errors(app)
    app.register_blueprint(home_blueprint)
    app.register_blueprint(auth_bp)
    app.register_blueprint(document_bp)
    app.register_blueprint(professor_bp)
    app.register_blueprint(aluno_bp)
