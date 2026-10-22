from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for

from app.controllers.professor_controller import (
    launch_activity,
    save_student_grade,
    upload_requested_document,
)
from app.routes.guards import teacher_required

professor_bp = Blueprint("professor", __name__)


@professor_bp.route("/professor", methods=["GET"])
@professor_bp.route("/professor/dashboard", methods=["GET"])
def dashboard():
    return render_template("spa.html")


@professor_bp.route("/professor/notas/salvar", methods=["POST"])
@professor_bp.route("/api/professor/notas/salvar", methods=["POST"])
def salvar_nota():
    teacher_required()
    from datetime import datetime
    from zoneinfo import ZoneInfo
    from app.database import get_session
    from app.models import ConfiguracaoModel
    with get_session() as db:
        config = db.get(ConfiguracaoModel, 'academico')
        prazo = config.valor.get('prazo_notas') if config else None
        if prazo and datetime.now(ZoneInfo('America/Sao_Paulo')).date().isoformat() > prazo:
            return jsonify(erro="O prazo de lançamento de notas foi encerrado pelo administrador."), 403
    response, status = save_student_grade(session.get("user_id"), request.form)
    if 200 <= status < 300 and not request.path.startswith("/api/"):
        return redirect(url_for("professor.dashboard"))

    return jsonify(response), status


@professor_bp.route("/professor/atividades/lancar", methods=["POST"])
@professor_bp.route("/api/professor/atividades/lancar", methods=["POST"])
def lancar_atividade():
    teacher_required()
    response, status = launch_activity(session.get("user_id"), request.form, request.files)
    if 200 <= status < 300 and not request.path.startswith("/api/"):
        return redirect(url_for("professor.dashboard"))

    return jsonify(response), status


@professor_bp.route("/professor/documentos/upload", methods=["POST"])
@professor_bp.route("/api/professor/documentos/upload", methods=["POST"])
def upload_documento_professor():
    teacher_required()
    response, status = upload_requested_document(
        session.get("user_id"),
        request.form,
        request.files,
    )
    if 200 <= status < 300 and not request.path.startswith("/api/"):
        return redirect(url_for("professor.dashboard"))

    return jsonify(response), status
