from flask import Blueprint, render_template, request

from app.routes import api_routes as api

home_blueprint = Blueprint("home", __name__)


@home_blueprint.route("/", methods=["GET"])
def home():
    return render_template("spa.html")


@home_blueprint.route("/dashboard", methods=["GET"])
@home_blueprint.route("/dashboard.html", methods=["GET"])
@home_blueprint.route("/admin/dashboard", methods=["GET"])
@home_blueprint.route("/admin_painel.html", methods=["GET"])
def admin_dashboard():
    return render_template("spa.html")


@home_blueprint.route("/cadastro/alunos", methods=["GET"])
@home_blueprint.route("/cadastro_aluno.html", methods=["GET"])
@home_blueprint.route("/admin/cadastro-alunos", methods=["GET"])
@home_blueprint.route("/admin_cadastro_aluno.html", methods=["GET"])
def admin_cadastro_alunos():
    return render_template("spa.html")


@home_blueprint.route("/cadastro/professores", methods=["GET"])
@home_blueprint.route("/cadastro_professores.html", methods=["GET"])
@home_blueprint.route("/admin/cadastro-professores", methods=["GET"])
@home_blueprint.route("/admin_cadastro_professores.html", methods=["GET"])
def admin_cadastro_professores():
    return render_template("spa.html")


@home_blueprint.route("/banco-de-dados", methods=["GET"])
@home_blueprint.route("/banco_de_dados.html", methods=["GET"])
@home_blueprint.route("/admin/banco-de-dados", methods=["GET"])
@home_blueprint.route("/admin_banco_dados.html", methods=["GET"])
def admin_banco_dados():
    return render_template("spa.html")


@home_blueprint.route("/comunicados", methods=["GET", "POST"])
@home_blueprint.route("/admin/comunicados", methods=["GET", "POST"])
@home_blueprint.route("/admin_comunicados.html", methods=["GET", "POST"])
def admin_comunicados():
    if request.method == "POST":
        return api.comunicados()
    return render_template("spa.html")


@home_blueprint.route("/disciplinas", methods=["GET", "POST"])
@home_blueprint.route("/admin/disciplinas", methods=["GET", "POST"])
@home_blueprint.route("/admin_disciplinas.html", methods=["GET", "POST"])
def admin_disciplinas():
    if request.method == "POST":
        return api.disciplinas()
    return render_template("spa.html")


@home_blueprint.route("/turmas", methods=["GET", "POST"])
@home_blueprint.route("/admin/turmas", methods=["GET", "POST"])
@home_blueprint.route("/admin_turmas.html", methods=["GET", "POST"])
def admin_turmas():
    if request.method == "POST":
        return api.turmas()
    return render_template("spa.html")


@home_blueprint.route("/admin/alunos/ultimo", defaults={"aluno_id": None})
@home_blueprint.route("/alunos/<int:aluno_id>", methods=["GET"])
@home_blueprint.route("/detalhes_aluno/<int:aluno_id>", methods=["GET"])
@home_blueprint.route("/admin/alunos/<int:aluno_id>", methods=["GET"])
@home_blueprint.route("/admin_detalhes_aluno/<int:aluno_id>", methods=["GET"])
def admin_detalhes_aluno(aluno_id):
    return render_template("spa.html")


@home_blueprint.route("/admin/alunos/<int:aluno_id>/documentos/solicitar", methods=["POST"])
def admin_solicitar_documento_aluno(aluno_id):
    return api.solicitar_documento_aluno(aluno_id)


@home_blueprint.route("/admin/alunos/<int:aluno_id>/editar", methods=["POST"])
def admin_editar_aluno(aluno_id):
    return api.editar_aluno(aluno_id)


@home_blueprint.route("/admin/professores/ultimo", defaults={"professor_id": None})
@home_blueprint.route("/professores/<int:professor_id>", methods=["GET"])
@home_blueprint.route("/detalhes_professor/<int:professor_id>", methods=["GET"])
@home_blueprint.route("/admin/professores/<int:professor_id>", methods=["GET"])
@home_blueprint.route("/admin_detalhes_professor/<int:professor_id>", methods=["GET"])
def admin_detalhes_professor(professor_id):
    return render_template("spa.html")


@home_blueprint.route("/admin/professores/<int:professor_id>/editar", methods=["POST"])
def admin_editar_professor(professor_id):
    return api.editar_professor(professor_id)


@home_blueprint.route("/admin/professores/<int:professor_id>/documentos/solicitar", methods=["POST"])
def admin_solicitar_documento_professor(professor_id):
    return api.solicitar_documento_professor(professor_id)


@home_blueprint.route("/detalhes_aluno.html", methods=["GET"])
@home_blueprint.route("/admin_detalhes_aluno.html", methods=["GET"])
def admin_detalhes_aluno_legacy():
    return render_template("spa.html")


@home_blueprint.route("/detalhes_professor.html", methods=["GET"])
@home_blueprint.route("/admin_detalhes_professor.html", methods=["GET"])
def admin_detalhes_professor_legacy():
    return render_template("spa.html")
