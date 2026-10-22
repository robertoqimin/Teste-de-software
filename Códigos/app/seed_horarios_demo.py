"""Adiciona horários apenas às turmas fictícias da carga demo, sem sobrescrever."""
from app import create_app
from app.database import get_session
from app.models import ConfiguracaoModel, DisciplinaModel, HorarioModel, TurmaDisciplinaModel, TurmaModel


def popular_horarios():
    create_app()
    quantidade = 0
    with get_session() as db:
        if not db.get(ConfiguracaoModel, 'carga_demo_v1'):
            print('Carga demo não encontrada; nenhum horário foi criado.')
            return
        for turma in db.query(TurmaModel).filter(TurmaModel.codigo.like('DEMO-T%')).all():
            vinculos = (db.query(TurmaDisciplinaModel).join(DisciplinaModel)
                .filter(TurmaDisciplinaModel.turma_id == turma.id, DisciplinaModel.codigo.like('DEMO-D%'))
                .order_by(DisciplinaModel.codigo).all())
            # Não acrescentar horários a turmas que já tenham uma grade cadastrada.
            if db.query(HorarioModel).filter(HorarioModel.turma_disciplina_id.in_([v.id for v in vinculos])).first():
                continue
            for i, vinculo in enumerate(vinculos):
                base = 7 * 60 if turma.turno == 'Matutino' else 13 * 60
                inicio = base + (i % 2) * 50
                fim = inicio + 50
                db.add(HorarioModel(turma_disciplina_id=vinculo.id, dia_semana=i // 2,
                    inicio=f'{inicio // 60:02d}:{inicio % 60:02d}', fim=f'{fim // 60:02d}:{fim % 60:02d}', demonstracao=True))
                quantidade += 1
        db.commit()
    print(f'{quantidade} horários de demonstração criados.')


if __name__ == '__main__':
    popular_horarios()
