from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for

from app.auth import professor_required
from app.controllers.auth_controller import buscar_alunos, cadastrar_usuario, login_usuario
from app.routes.guards import admin_json_required

auth_bp = Blueprint('auth', __name__)


def _admin_session_required():
    return admin_json_required()


def _get_request_data():
    if request.form:
        return request.form.copy()

    return request.get_json(silent=True) or {}


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template("spa.html")
    data = request.get_json(silent=True)
    response, status = login_usuario(data)
    if status == 200:
        session.clear()
        session["versao_sessao"] = response["versao_sessao"]
        session["user_id"] = response["id"]
        session["user_email"] = response["email"]
        session["user_role"] = response["role"]

    return jsonify(response), status


@auth_bp.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for("home.home"))


@auth_bp.route('/cadastro', methods=['POST'])
def cadastro():
    error = _admin_session_required()
    if error:
        return error
    data = _get_request_data()
    response, status = cadastrar_usuario(data, request.files)
    return jsonify(response), status


@auth_bp.route('/cadastro/aluno', methods=['POST'])
@auth_bp.route('/cadastro/alunos', methods=['POST'])
@auth_bp.route("/api/cadastro/aluno", methods=["POST"])
def cadastro_aluno():
    error_response = _admin_session_required()
    if error_response:
        return error_response

    data = _get_request_data()
    data["tipo"] = "aluno"
    response, status = cadastrar_usuario(data, request.files)
    return jsonify(response), status


@auth_bp.route('/cadastro/professor', methods=['POST'])
@auth_bp.route('/cadastro/professores', methods=['POST'])
@auth_bp.route("/api/cadastro/professor", methods=["POST"])
def cadastro_professor():
    error_response = _admin_session_required()
    if error_response:
        return error_response

    data = _get_request_data()
    data["tipo"] = "professor"
    response, status = cadastrar_usuario(data, request.files)
    return jsonify(response), status


@auth_bp.route('/professor/teste', methods=['GET'])
@professor_required
def teste_professor():
    # Rota simples para validar se o JWT pertence a um professor.
    return jsonify({"mensagem": "Permissao de professor validada"}), 200


@auth_bp.route('/alunos/busca', methods=['GET'])
@professor_required
def alunos_busca():
    termo = request.args.get("termo") or request.args.get("q") or request.args.get("cpf")
    response, status = buscar_alunos(termo)
    return jsonify(response), status


@auth_bp.route('/api/senha', methods=['POST'])
def alterar_senha():
    from app.database import get_session
    from app.models import UsuarioModel
    from app.governanca import auditar
    from werkzeug.security import check_password_hash, generate_password_hash
    if not session.get('user_id'):
        return jsonify(erro="Entre novamente."), 401
    data = request.get_json(silent=True) or {}
    nova = data.get('nova_senha', '')
    if not isinstance(nova, str) or len(nova) < 8:
        return jsonify(erro="Use uma senha com pelo menos 8 caracteres."), 400
    with get_session() as db:
        user = db.get(UsuarioModel, session['user_id'])
        if not check_password_hash(user.senha, data.get('senha_atual', '')):
            return jsonify(erro="Senha atual inválida."), 403
        if check_password_hash(user.senha, nova):
            return jsonify(erro="Escolha uma senha diferente da atual."), 400
        user.senha = generate_password_hash(nova)
        user.exigir_troca = False
        user.versao_sessao += 1
        session['versao_sessao'] = user.versao_sessao
        session['exigir_troca'] = False
        auditar(db, 'Senha alterada pelo usuário')
        db.commit()
    return jsonify(mensagem="Senha alterada.")
