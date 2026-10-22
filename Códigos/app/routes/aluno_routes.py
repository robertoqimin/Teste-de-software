from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for
from werkzeug.datastructures import MultiDict

from app.controllers.document_controller import upload_documento
from app.controllers.aluno_controller import (
    get_aluno_by_user_id,
    get_aluno_document_request,
    marcar_documento_aluno_enviado,
)
from app.routes.guards import aluno_required

aluno_bp = Blueprint("aluno", __name__)


@aluno_bp.route("/aluno", methods=["GET"])
@aluno_bp.route("/aluno/dashboard", methods=["GET"])
def dashboard():
    return render_template("spa.html")


@aluno_bp.route("/aluno/disciplinas/<int:disciplina_id>", methods=["GET"])
def disciplina_detail(disciplina_id):
    return render_template("spa.html")


@aluno_bp.route("/aluno/documentos/upload", methods=["POST"])
@aluno_bp.route("/api/aluno/documentos/upload", methods=["POST"])
def upload_documento_aluno():
    aluno_required()
    aluno = get_aluno_by_user_id(session.get("user_id"))
    if not aluno:
        return jsonify({"erro": "Aluno nao encontrado"}), 404

    solicitacao_id = request.form.get("solicitacao_id", type=int)
    if not solicitacao_id:
        return jsonify({"erro": "Solicitacao de documento nao informada"}), 400

    solicitacao = get_aluno_document_request(solicitacao_id, aluno["id"])
    if not solicitacao:
        return jsonify({"erro": "Solicitacao de documento nao encontrada"}), 404

    upload_form = MultiDict(request.form)
    upload_form["titulo"] = solicitacao["titulo"]

    response, status = upload_documento(
        upload_form,
        request.files,
        is_admin=True,
        aluno_id_override=aluno["id"],
    )

    if 200 <= status < 300:
        marcar_documento_aluno_enviado(
            solicitacao_id,
            aluno["id"],
            response["documento"]["id"],
        )
        if not request.path.startswith("/api/"):
            return redirect(url_for("aluno.dashboard"))

    return jsonify(response), status


@aluno_bp.route('/api/aluno/atividades/<int:atividade_id>/enviar', methods=['POST'])
def enviar_atividade(atividade_id):
    aluno_required()
    from app.controllers.document_controller import enviar_atividade_aluno
    response, status = enviar_atividade_aluno(session['user_id'], atividade_id, request.files)
    return jsonify(response), status
