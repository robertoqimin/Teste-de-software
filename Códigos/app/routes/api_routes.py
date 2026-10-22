"""JSON da SPA. As regras de negócio e permissões continuam no servidor."""
from flask import Blueprint, abort, jsonify, request, session
from werkzeug.exceptions import HTTPException

from app.auth import normalize_role
from app.controllers import admin_controller as admin
from app.controllers.aluno_controller import get_aluno_area_data, get_aluno_disciplina_detail
from app.controllers.professor_controller import get_teacher_area_data
from app.routes.guards import admin_required, aluno_required, teacher_required

api_bp = Blueprint("api", __name__, url_prefix="/api")


def require_session():
    if request.path.startswith("/api/") and request.endpoint != "api.current_session" and not session.get("user_id"):
        return jsonify(erro="Sua sessão expirou. Entre novamente."), 401


@api_bp.route("/session")
def current_session():
    if not session.get("user_id"):
        return jsonify(user=None)
    return jsonify(user={
        "id": session["user_id"],
        "email": session.get("user_email"),
        "role": normalize_role(session.get("user_role")),
    })


@api_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify(mensagem="Sessão encerrada.")


@api_bp.route("/admin/dashboard")
@api_bp.route("/admin/banco-de-dados")
def admin_data():
    admin_required()
    return jsonify(admin.get_admin_data())


@api_bp.route("/admin/comunicados", methods=["GET", "POST"])
def comunicados():
    admin_required()
    if request.method == "POST":
        result, status = admin.criar_comunicado(request.form, session.get("user_email"))
        return jsonify(result), status
    return jsonify(comunicados=admin.get_comunicados())


@api_bp.route("/admin/disciplinas", methods=["GET", "POST"])
def disciplinas():
    admin_required()
    if request.method == "POST":
        action = request.form.get("action", "create")
        operations = {"create": admin.criar_disciplina, "associate_teacher": admin.associar_professor_disciplina}
        if action not in operations:
            return jsonify(erro="Ação de disciplina inválida."), 400
        result, status = operations[action](request.form)
        return jsonify(result), status
    return jsonify(admin.get_disciplinas_page_data())


@api_bp.route("/admin/turmas", methods=["GET", "POST"])
def turmas():
    admin_required()
    if request.method == "POST":
        action = request.form.get("action", "create")
        operations = {
            "create": admin.criar_turma,
            "associate_student": admin.associar_aluno_turma,
            "associate_teacher": admin.associar_professor_turma,
        }
        if action not in operations:
            return jsonify(erro="Ação de turma inválida."), 400
        result, status = operations[action](request.form)
        return jsonify(result), status
    return jsonify(admin.get_turmas_page_data())


@api_bp.route("/admin/alunos/<int:aluno_id>")
@api_bp.route("/admin/alunos/ultimo", defaults={"aluno_id": None})
def aluno_detail(aluno_id):
    admin_required()
    return jsonify(admin.get_aluno_detail(aluno_id))


@api_bp.route("/admin/professores/<int:professor_id>")
@api_bp.route("/admin/professores/ultimo", defaults={"professor_id": None})
def professor_detail(professor_id):
    admin_required()
    return jsonify(admin.get_professor_detail(professor_id))


@api_bp.route("/admin/alunos/<int:aluno_id>/editar", methods=["POST"])
def editar_aluno(aluno_id):
    admin_required()
    result, status = admin.update_student_data(aluno_id, request.form, request.files)
    return jsonify(result), status


@api_bp.route("/admin/professores/<int:professor_id>/editar", methods=["POST"])
def editar_professor(professor_id):
    admin_required()
    result, status = admin.update_professor_data(professor_id, request.form, request.files)
    return jsonify(result), status


@api_bp.route("/admin/alunos/<int:aluno_id>/documentos/solicitar", methods=["POST"])
def solicitar_documento_aluno(aluno_id):
    admin_required()
    result, status = admin.request_student_document(aluno_id, request.form)
    return jsonify(result), status


@api_bp.route("/admin/professores/<int:professor_id>/documentos/solicitar", methods=["POST"])
def solicitar_documento_professor(professor_id):
    admin_required()
    result, status = admin.request_professor_document(professor_id, request.form)
    return jsonify(result), status


@api_bp.route("/aluno")
def aluno_data():
    aluno_required()
    data = get_aluno_area_data(session["user_id"])
    if not data:
        abort(404)
    return jsonify(data)


@api_bp.route("/aluno/disciplinas/<int:disciplina_id>")
def aluno_disciplina(disciplina_id):
    aluno_required()
    data = get_aluno_disciplina_detail(session["user_id"], disciplina_id)
    if not data:
        abort(404)
    return jsonify(data)


@api_bp.route("/professor")
def professor_data():
    teacher_required()
    data = get_teacher_area_data(session["user_id"])
    if not data:
        abort(404)
    return jsonify(data)


def register_api_errors(app):
    app.before_request(require_session)

    @app.after_request
    def private_api_response(response):
        if request.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.errorhandler(HTTPException)
    def api_http_error(error):
        if request.path.startswith("/api/") or request.accept_mimetypes.best == "application/json":
            response = error.get_response()
            response.data = app.json.dumps({"erro": {
                400: "Dados inválidos.", 401: "Entre novamente para continuar.",
                403: "Você não tem permissão para esta operação.",
                404: "Registro ou página não encontrado.",
                405: "Método não permitido.",
            }.get(error.code, error.description)})
            response.content_type = "application/json"
            response.headers["Cache-Control"] = "no-store"
            return response
        return error
