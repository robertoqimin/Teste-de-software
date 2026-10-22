import csv
import io
from datetime import date
from flask import Blueprint, abort, jsonify, request, session, render_template, Response
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.security import generate_password_hash
from app.database import get_session
from app.models import UsuarioModel, AuditoriaModel, ConfiguracaoModel, AlunoModel, ProfessorModel, TurmaModel, SolicitacaoDocumentoModel
from app.governanca import PERMISSOES, auditar

gestao_bp = Blueprint('gestao', __name__)


@gestao_bp.before_request
def proteger():
    if request.path.startswith('/api/gestao/') and session.get('user_role') != 'admin':
        abort(403)


@gestao_bp.route('/gestao')
def pagina():
    return render_template('spa.html')


def usuario_json(user):
    return dict(id=user.id, email=user.email, role=user.tipo.lower(), ativo=user.ativo, exigir_troca=user.exigir_troca, permissoes={k: (user.permissoes or {}).get(k, True) for k in PERMISSOES})


@gestao_bp.route('/api/gestao/painel')
def painel():
    from app.pagination import page_options, page_info
    page, size = page_options()
    with get_session() as db:
        query = db.query(UsuarioModel)
        search = request.args.get('search', '').strip()
        if search:
            query = query.filter(UsuarioModel.email.contains(search, autoescape=True))
        role = request.args.get('role', '')
        if role:
            query = query.filter(func.lower(UsuarioModel.tipo) == role)
        pagination = page_info(page, size, query.count())
        users = query.order_by(UsuarioModel.id).offset((pagination['page'] - 1) * size).limit(size).all()
        return jsonify(usuarios=[usuario_json(u) for u in users], pagination=pagination, permissoes=PERMISSOES,
            resumo=dict(alunos=db.query(AlunoModel).count(), professores=db.query(ProfessorModel).count(), turmas=db.query(TurmaModel).count(), contas_bloqueadas=db.query(UsuarioModel).filter_by(ativo=False).count(), documentos_pendentes=db.query(SolicitacaoDocumentoModel).filter_by(status="pendente").count()),
            auditoria=[dict(id=a.id, email=a.email, acao=a.acao, detalhes=a.detalhes, data=a.data.isoformat()) for a in db.query(AuditoriaModel).order_by(AuditoriaModel.id.desc()).limit(100)],
            configuracoes=(db.get(ConfiguracaoModel, 'academico').valor if db.get(ConfiguracaoModel, 'academico') else {}))


@gestao_bp.route('/api/gestao/usuarios', methods=['POST'])
@gestao_bp.route('/api/gestao/usuarios/<int:user_id>', methods=['POST'])
def salvar_usuario(user_id=None):
    data = request.get_json(silent=True) or {}
    with get_session() as db:
        user = db.get(UsuarioModel, user_id) if user_id else UsuarioModel(tipo='secretaria')
        if not user:
            abort(404)
        antes = usuario_json(user) if user_id else None
        if user_id == session['user_id']:
            return jsonify(erro='Altere sua conta usando outro administrador para evitar perder o acesso.'), 400
        if user.tipo.lower() not in {'admin', 'secretaria'}:
            if set(data) - {'ativo', 'encerrar_sessoes', 'senha', 'exigir_troca'}:
                return jsonify(erro='O perfil acadêmico deve ser editado pela secretaria.'), 400
        else:
            role = data.get('role', user.tipo).lower()
            if role not in {'admin', 'secretaria'}:
                return jsonify(erro='Perfil inválido.'), 400
            user.tipo = role
            email = str(data.get('email', user.email or '')).strip().lower()
            if '@' not in email or len(email) > 120:
                return jsonify(erro='Informe um e-mail válido.'), 400
            user.email = email
            permissions = data.get('permissoes', user.permissoes or {})
            if not isinstance(permissions, dict) or any(k not in PERMISSOES or type(v) is not bool for k, v in permissions.items()):
                return jsonify(erro='Permissões inválidas.'), 400
            user.permissoes = permissions
        senha = data.get('senha')
        if not user_id and not senha:
            return jsonify(erro='Informe uma senha inicial.'), 400
        if senha:
            if not isinstance(senha, str) or len(senha) < 8:
                return jsonify(erro='Use uma senha com pelo menos 8 caracteres.'), 400
            user.senha = generate_password_hash(senha)
        if 'ativo' in data and type(data['ativo']) is not bool:
            return jsonify(erro='Status inválido.'), 400
        if 'exigir_troca' in data and type(data['exigir_troca']) is not bool:
            return jsonify(erro='Opção de troca de senha inválida.'), 400
        user.exigir_troca = data.get('exigir_troca', user.exigir_troca if user_id else True)
        user.ativo = data.get('ativo', True if not user_id else user.ativo)
        user.versao_sessao = (user.versao_sessao or 0) + 1
        db.add(user)
        try:
            db.flush()
            auditar(db, 'Conta atualizada' if user_id else 'Conta criada', {'usuario_id': user.id, 'antes': antes, 'depois': usuario_json(user)})
            db.commit()
        except IntegrityError:
            db.rollback()
            return jsonify(erro='E-mail já cadastrado.'), 409
        return jsonify(mensagem='Conta salva. Sessões anteriores foram encerradas.'), 200 if user_id else 201


@gestao_bp.route('/api/gestao/configuracoes', methods=['POST'])
def configuracoes():
    data = request.get_json(silent=True) or {}
    try:
        values = dict(ano_letivo=int(data['ano_letivo']), periodos=int(data['periodos']), media_aprovacao=float(data['media_aprovacao']), prazo_notas=str(data.get('prazo_notas', '')))
        if not 2000 <= values['ano_letivo'] <= 2200 or not 1 <= values['periodos'] <= 12 or not 0 <= values['media_aprovacao'] <= 10:
            raise ValueError()
        if values['prazo_notas']:
            date.fromisoformat(values['prazo_notas'])
    except (ValueError, KeyError, TypeError):
        return jsonify(erro='Configurações acadêmicas inválidas.'), 400
    with get_session() as db:
        config = db.get(ConfiguracaoModel, 'academico')
        antes = config.valor if config else {}
        if config:
            config.valor = values
        else:
            db.add(ConfiguracaoModel(chave='academico', valor=values))
        auditar(db, 'Configurações acadêmicas alteradas', {'antes': antes, 'depois': values})
        db.commit()
    return jsonify(mensagem='Configurações salvas.')


@gestao_bp.route('/api/gestao/relatorio.csv')
def relatorio():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'E-mail', 'Perfil', 'Ativo'])
    with get_session() as db:
        for user in db.query(UsuarioModel).order_by(UsuarioModel.id):
            email = user.email
            if email.startswith(('=', '+', '-', '@')):
                email = "'" + email
            writer.writerow([user.id, email, user.tipo, user.ativo])
        auditar(db, 'Relatório de usuários exportado')
        db.commit()
    return Response('\ufeff' + output.getvalue(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=usuarios.csv'})


@gestao_bp.route('/api/gestao/backup')
def backup():
    import json
    from datetime import datetime, timezone
    from app.database import Base, engine
    with engine.begin() as connection:
        tables = {table.name: [dict(row) for row in connection.execute(table.select()).mappings()] for table in Base.metadata.sorted_tables}
    with get_session() as db:
        auditar(db, 'Backup do banco exportado')
        db.commit()
    payload = dict(formato='secretaria-db-v1', data=datetime.now(timezone.utc).isoformat(), tabelas=tables)
    return Response(json.dumps(payload, default=str, ensure_ascii=False), mimetype='application/json', headers={'Content-Disposition': 'attachment; filename=secretaria-backup.json'})


@gestao_bp.route('/api/gestao/restaurar', methods=['POST'])
def restaurar():
    request.max_content_length = 33 * 1024 * 1024
    import json
    import secrets
    from datetime import datetime, date, timezone
    from decimal import Decimal, InvalidOperation
    from sqlalchemy import DateTime, Date, Numeric
    from werkzeug.security import check_password_hash
    from app.database import Base, engine
    if request.form.get('confirmacao') != 'RESTAURAR':
        return jsonify(erro='Digite RESTAURAR para confirmar.'), 400
    with get_session() as db:
        current = db.get(UsuarioModel, session['user_id'])
        if not check_password_hash(current.senha, request.form.get('senha', '')):
            return jsonify(erro='Senha do administrador inválida.'), 403
    arquivo = request.files.get('backup')
    if not arquivo:
        return jsonify(erro='Selecione o backup.'), 400
    raw = arquivo.read(32 * 1024 * 1024 + 1)
    if len(raw) > 32 * 1024 * 1024:
        return jsonify(erro='Backup deve ter até 32 MB.'), 400
    try:
        payload = json.loads(raw)
        tables = Base.metadata.sorted_tables
        if payload['formato'] != 'secretaria-db-v1' or set(payload['tabelas']) != {t.name for t in tables}:
            raise ValueError()
        rows_by_table = payload['tabelas']
        if not any(u['tipo'].lower() == 'admin' and u['ativo'] for u in rows_by_table['usuarios']):
            return jsonify(erro='O backup precisa conter um administrador ativo.'), 400
        if not any(c['chave'] == 'migracao_secretaria_v1' for c in rows_by_table['configuracoes']):
            raise ValueError()
        for table in tables:
            for row in rows_by_table[table.name]:
                if set(row) != set(table.columns.keys()):
                    raise ValueError()
                for column in table.columns:
                    value = row[column.name]
                    if value is not None:
                        if isinstance(column.type, DateTime):
                            row[column.name] = datetime.fromisoformat(value)
                        elif isinstance(column.type, Date):
                            row[column.name] = date.fromisoformat(value)
                        elif isinstance(column.type, Numeric):
                            row[column.name] = Decimal(str(value))
        for user in rows_by_table['usuarios']:
            user['versao_sessao'] = secrets.randbelow(2**30)
    except (ValueError, KeyError, TypeError, AttributeError, InvalidOperation):
        return jsonify(erro='Backup inválido ou incompatível.'), 400
    try:
        with engine.begin() as connection:
            for table in reversed(tables):
                connection.execute(table.delete())
            for table in tables:
                if rows_by_table[table.name]:
                    connection.execute(table.insert(), rows_by_table[table.name])
            connection.execute(AuditoriaModel.__table__.insert().values(usuario_id=session['user_id'], email=session['user_email'], acao='Banco restaurado', detalhes={}, data=datetime.now(timezone.utc)))
    except (SQLAlchemyError, ValueError, TypeError):
        return jsonify(erro='Não foi possível restaurar. O banco anterior foi preservado.'), 400
    session.clear()
    return jsonify(mensagem='Banco restaurado. Entre novamente com uma conta do backup.')


@gestao_bp.route('/api/gestao/academico.csv')
def relatorio_academico():
    from app.models import NotaModel, DisciplinaModel
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Matrícula', 'Aluno', 'Série/curso', 'Status', 'Disciplina', 'Nota'])
    with get_session() as db:
        rows = (db.query(AlunoModel, NotaModel, DisciplinaModel)
                .outerjoin(NotaModel, NotaModel.aluno_id == AlunoModel.id)
                .outerjoin(DisciplinaModel, DisciplinaModel.id == NotaModel.disciplina_id)
                .order_by(AlunoModel.id).all())
        for aluno, nota, disciplina in rows:
            values = [aluno.matricula, aluno.nome, aluno.curso_serie, aluno.status_matricula, disciplina.nome if disciplina else '', str(nota.nota) if nota else '']
            writer.writerow([("'" + value) if isinstance(value, str) and value.startswith(('=', '+', '-', '@')) else value for value in values])
        auditar(db, 'Relatório acadêmico exportado')
        db.commit()
    return Response('\ufeff' + output.getvalue(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=academico.csv'})
