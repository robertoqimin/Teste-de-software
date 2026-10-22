import re
from sqlalchemy.exc import IntegrityError
from app.database import get_session
from app.models import HorarioModel, TurmaDisciplinaModel, TurmaModel, DisciplinaModel
from app.governanca import auditar


def dados_cronograma():
    with get_session() as db:
        disciplinas = [dict(id=d.id, nome=d.nome, codigo=d.codigo, carga_horaria=d.carga_horaria)
                       for d in db.query(DisciplinaModel).order_by(DisciplinaModel.nome)]
        horarios = [dict(id=h.id, turma_id=v.turma_id, disciplina_id=v.disciplina_id,
                        turma=t.nome, dia_semana=h.dia_semana, inicio=h.inicio, fim=h.fim, demonstracao=h.demonstracao)
                    for h, v, t in db.query(HorarioModel, TurmaDisciplinaModel, TurmaModel)
                    .join(TurmaDisciplinaModel, TurmaDisciplinaModel.id == HorarioModel.turma_disciplina_id)
                    .join(TurmaModel, TurmaModel.id == TurmaDisciplinaModel.turma_id)
                    .order_by(HorarioModel.dia_semana, HorarioModel.inicio).all()]
        return dict(disciplinas=disciplinas, horarios=horarios)


def salvar_horario(data):
    try:
        turma_id = int(data.get('turma_id', ''))
        disciplina_id = int(data.get('disciplina_id', ''))
        horario_id = int(data.get('horario_id') or 0)
        dias = sorted(set(int(d) for d in data.getlist('dias')))
        inicio, fim = data.get('inicio', ''), data.get('fim', '')
        if not dias or any(d < 0 or d > 5 for d in dias) or (horario_id and len(dias) != 1):
            raise ValueError()
        if not all(re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d', h) for h in (inicio, fim)) or inicio >= fim:
            raise ValueError()
    except (ValueError, TypeError):
        return {'erro': 'Informe turma, disciplina, dias válidos e horário final após o inicial.'}, 400
    with get_session() as db:
        # Serializa alterações da grade de uma turma para evitar conflitos concorrentes.
        turma = db.query(TurmaModel).filter_by(id=turma_id).with_for_update().first()
        if not turma or not db.get(DisciplinaModel, disciplina_id):
            return {'erro': 'Turma ou disciplina não encontrada.'}, 404
        existente = db.get(HorarioModel, horario_id) if horario_id else None
        if horario_id and (not existente or db.get(TurmaDisciplinaModel, existente.turma_disciplina_id).turma_id != turma_id):
            return {'erro': 'Horário não encontrado nesta turma.'}, 404
        conflitos = (db.query(HorarioModel).join(TurmaDisciplinaModel)
            .filter(TurmaDisciplinaModel.turma_id == turma_id, HorarioModel.dia_semana.in_(dias),
                    HorarioModel.inicio < fim, HorarioModel.fim > inicio, HorarioModel.id != horario_id).first())
        if conflitos:
            return {'erro': 'A turma já possui aula nesse intervalo em um dos dias selecionados.'}, 409
        vinculo = db.query(TurmaDisciplinaModel).filter_by(turma_id=turma_id, disciplina_id=disciplina_id).first()
        if not vinculo:
            vinculo = TurmaDisciplinaModel(turma_id=turma_id, disciplina_id=disciplina_id)
            db.add(vinculo)
            db.flush()
        antes = dict(dia_semana=existente.dia_semana, inicio=existente.inicio, fim=existente.fim,
                     turma_disciplina_id=existente.turma_disciplina_id) if existente else None
        for dia in dias:
            horario = existente or HorarioModel()
            horario.turma_disciplina_id = vinculo.id
            horario.dia_semana, horario.inicio, horario.fim = dia, inicio, fim
            horario.demonstracao = False
            db.add(horario)
        auditar(db, 'Cronograma da turma alterado', dict(turma_id=turma_id, disciplina_id=disciplina_id,
                antes=antes, depois=dict(dias=dias, inicio=inicio, fim=fim)))
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            return {'erro': 'Conflito ao salvar o horário. Atualize a grade e tente novamente.'}, 409
    return {'mensagem': 'Disciplina vinculada à turma e cronograma salvo.'}, 200


def remover_horario(data):
    try:
        horario_id = int(data.get('horario_id', ''))
    except (ValueError, TypeError):
        return {'erro': 'Horário inválido.'}, 400
    with get_session() as db:
        horario = db.get(HorarioModel, horario_id)
        if not horario:
            return {'erro': 'Horário não encontrado.'}, 404
        turma_id = db.get(TurmaDisciplinaModel, horario.turma_disciplina_id).turma_id
        db.query(TurmaModel).filter_by(id=turma_id).with_for_update().first()
        auditar(db, 'Horário removido', dict(horario_id=horario.id, turma_id=turma_id,
                dia_semana=horario.dia_semana, inicio=horario.inicio, fim=horario.fim))
        db.delete(horario)
        db.commit()
    return {'mensagem': 'Horário removido. A disciplina continua vinculada à turma.'}, 200
