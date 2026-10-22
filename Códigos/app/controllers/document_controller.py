import os
from uuid import uuid4

from flask import current_app
from werkzeug.utils import secure_filename

from app.database import get_session
from app.models import AlunoModel, DisciplinaModel, DocumentoModel, ProfessorModel


def get_upload_folder():
    return os.path.abspath(current_app.config["UPLOAD_FOLDER"])


def _get_or_create_disciplina(session_db, disciplina_id=None):
    if disciplina_id:
        disciplina = session_db.get(DisciplinaModel, disciplina_id)
        if disciplina:
            return disciplina, None

        return None, ({"erro": "Disciplina nao encontrada"}, 404)

    disciplina = (
        session_db.query(DisciplinaModel)
        .filter(DisciplinaModel.codigo == "GERAL")
        .first()
    )
    if disciplina:
        return disciplina, None

    disciplina = DisciplinaModel(
        nome="Geral",
        codigo="GERAL",
        carga_horaria=0,
    )
    session_db.add(disciplina)
    session_db.flush()
    return disciplina, None


def upload_documento(form, files, current_user=None, is_admin=False, aluno_id_override=None):
    if "arquivo" not in files:
        return {"erro": "Arquivo nao enviado"}, 400

    aluno_id = aluno_id_override or form.get("aluno_id", type=int)
    if not aluno_id:
        return {"erro": "aluno_id e obrigatorio"}, 400

    arquivo = files["arquivo"]
    if not arquivo.filename:
        return {"erro": "Nome do arquivo nao informado"}, 400

    session_db = get_session()
    upload_folder = get_upload_folder()
    os.makedirs(upload_folder, exist_ok=True)
    saved_path = None

    try:
        aluno = session_db.get(AlunoModel, aluno_id)
        if not aluno:
            return {"erro": "Aluno nao encontrado"}, 404

        professor = None
        if not is_admin and current_user:
            professor = (
                session_db.query(ProfessorModel)
                .filter(ProfessorModel.usuario_id == int(current_user["sub"]))
                .first()
            )
            if not professor:
                return {"erro": "Professor nao encontrado para o usuario autenticado"}, 403

        disciplina, error = _get_or_create_disciplina(
            session_db,
            form.get("disciplina_id", type=int),
        )
        if error:
            return error

        original_filename = secure_filename(arquivo.filename)
        if not original_filename:
            return {"erro": "Nome do arquivo invalido"}, 400

        filename = f"{uuid4().hex}_{original_filename}"
        saved_path = os.path.join(upload_folder, filename)
        arquivo.save(saved_path)

        documento = DocumentoModel(
            aluno_id=aluno.id,
            professor_id=professor.id if professor else None,
            disciplina_id=disciplina.id,
            titulo=(form.get("titulo") or original_filename)[:150],
            caminho_arquivo=filename,
        )
        session_db.add(documento)
        session_db.commit()

        return {
            "mensagem": "Arquivo enviado",
            "documento": {
                "id": documento.id,
                "titulo": documento.titulo,
                "arquivo": documento.caminho_arquivo,
                "aluno_id": documento.aluno_id,
                "professor_id": documento.professor_id,
                "disciplina_id": documento.disciplina_id,
            },
        }, 201
    except Exception:
        session_db.rollback()
        if saved_path and os.path.exists(saved_path):
            os.remove(saved_path)
        raise
    finally:
        session_db.close()


def enviar_atividade_aluno(user_id, atividade_id, files):
    from app.models import AtividadeModel, AlunoTurmaModel, TurmaDisciplinaModel
    arquivo = files.get('arquivo')
    if not arquivo or not arquivo.filename:
        return {"erro": "Selecione o arquivo da atividade."}, 400
    original = secure_filename(arquivo.filename)
    if not original:
        return {"erro": "Nome do arquivo inválido."}, 400
    saved_path = None
    with get_session() as db:
        try:
            aluno = db.query(AlunoModel).filter_by(usuario_id=user_id).first()
            atividade = db.get(AtividadeModel, atividade_id)
            if not aluno or not atividade:
                return {"erro": "Atividade não encontrada."}, 404
            if atividade.tipo != "atividade":
                return {"erro": "Conteúdos não recebem entregas."}, 400
            vinculo = db.query(AlunoTurmaModel).join(
                TurmaDisciplinaModel, TurmaDisciplinaModel.turma_id == AlunoTurmaModel.turma_id
            ).filter(AlunoTurmaModel.aluno_id == aluno.id,
                     AlunoTurmaModel.turma_id == atividade.turma_id,
                     TurmaDisciplinaModel.disciplina_id == atividade.disciplina_id).first()
            if not vinculo:
                return {"erro": "Atividade não encontrada para este aluno."}, 404
            folder = get_upload_folder()
            os.makedirs(folder, exist_ok=True)
            filename = f"entrega_{uuid4().hex}_{original[-180:]}"
            saved_path = os.path.join(folder, filename)
            arquivo.save(saved_path)
            documento = DocumentoModel(aluno_id=aluno.id, professor_id=atividade.professor_id,
                disciplina_id=atividade.disciplina_id, atividade_id=atividade.id,
                titulo=atividade.titulo, caminho_arquivo=filename)
            db.add(documento)
            db.commit()
            return {"mensagem": "Atividade enviada com sucesso.", "id": documento.id}, 201
        except Exception:
            db.rollback()
            if saved_path and os.path.exists(saved_path):
                os.remove(saved_path)
            raise
