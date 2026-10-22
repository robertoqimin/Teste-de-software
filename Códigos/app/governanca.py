from flask import session, request, jsonify, has_request_context
from sqlalchemy import event, inspect
from app.database import get_session, SessionLocal
from app.models import UsuarioModel, AuditoriaModel, AlunoModel, ProfessorModel
from app.auth import normalize_role

PERMISSOES = {"cadastros": "Cadastrar e editar pessoas", "academico": "Gerenciar turmas e disciplinas", "documentos": "Gerenciar documentos", "comunicados": "Publicar comunicados"}


def validar_sessao():
    if not session.get("user_id"):
        return None
    with get_session() as db:
        user = db.get(UsuarioModel, session["user_id"])
        if not user or not user.ativo or user.versao_sessao != session.get("versao_sessao", 0):
            session.clear()
            if request.path == '/api/session':
                return jsonify(user=None)
            return jsonify(erro="Sua sessão expirou. Entre novamente."), 401
        session["exigir_troca"] = user.exigir_troca
        if user.exigir_troca and request.path not in {'/api/session', '/api/senha', '/api/logout', '/login', '/logout'} and (request.path.startswith('/api/') or request.method != 'GET'):
            return jsonify(erro="Altere sua senha para continuar."), 403
        session["user_role"] = normalize_role(user.tipo)
        session["user_email"] = user.email
        session["permissoes"] = user.permissoes or {}
    if session["user_role"] == "secretaria" and request.method in {"POST", "PUT", "DELETE", "PATCH"}:
        path = request.path
        permission = None
        if 'cadastro' in path or path.endswith('/editar'):
            permission = 'cadastros'
        elif 'documentos' in path or 'arquivos' in path:
            permission = 'documentos'
        elif 'turmas' in path or 'disciplinas' in path:
            permission = 'academico'
        elif 'comunicados' in path:
            permission = 'comunicados'
        if permission and session['permissoes'].get(permission, True) is not True:
            return jsonify(erro="Sua conta não tem permissão para esta operação."), 403


def auditar(db, acao, detalhes=None):
    db.add(AuditoriaModel(usuario_id=session.get('user_id'), email=session.get('user_email', 'anônimo'), acao=acao[:255], detalhes=detalhes or {}))


def registrar_operacao(response):
    if request.method in {'POST', 'PUT', 'PATCH', 'DELETE'} and request.path != '/api/logout':
        with get_session() as db:
            # Nunca persistir senhas, tokens, arquivos ou corpo bruto de formulários.
            detalhes = {'status': response.status_code}
            if request.path == '/login':
                data = request.get_json(silent=True) or {}
                if isinstance(data, dict):
                    detalhes['email_informado'] = str(data.get('email', ''))[:120]
            auditar(db, f'{request.method} {request.path}', detalhes)
            db.commit()
    return response


# Registra alterações de cadastro na mesma transação que os dados alterados.
@event.listens_for(SessionLocal, 'before_flush')
def auditar_cadastros(db, flush_context, instances):
    if not has_request_context() or not session.get('user_id'):
        return
    for obj in list(db.dirty):
        if not isinstance(obj, (AlunoModel, ProfessorModel)):
            continue
        alteracoes = {}
        for column in inspect(obj).mapper.column_attrs:
            history = inspect(obj).attrs[column.key].history
            if history.has_changes():
                alteracoes[column.key] = {
                    'antes': str(history.deleted[0]) if history.deleted and history.deleted[0] is not None else None,
                    'depois': str(history.added[0]) if history.added and history.added[0] is not None else None,
                }
        if alteracoes:
            auditar(db, 'Cadastro alterado', {'entidade': obj.__tablename__, 'id': obj.id, 'alteracoes': alteracoes})
