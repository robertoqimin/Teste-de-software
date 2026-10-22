"""Valida a carga completa sem acessar o banco da instalação."""
import contextlib
import io
import os
import sys
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory(prefix='secretaria-carga-test-') as pasta:
    os.environ['DB_URL'] = 'sqlite:///' + str(Path(pasta) / 'test.db')
    os.environ['UPLOAD_FOLDER'] = str(Path(pasta) / 'uploads')
    os.environ['SECRET_KEY'] = 'test-only-secret'
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from app.seed_demo import popular, contagens
    from app.database import engine
    from sqlalchemy import text
    with contextlib.redirect_stdout(io.StringIO()):
        popular()
        antes = contagens()
        popular()
    assert contagens() == antes, 'Reexecução duplicou registros'
    assert antes['alunos'] == 800 and antes['professores'] == 200
    assert antes['usuarios'] == 1000
    assert antes['notas'] == 8000 and antes['alunos_disciplinas'] == 8000
    assert all(antes.values()), 'Alguma tabela ficou vazia'
    from app.controllers.admin_controller import get_turmas_page_data
    turmas = get_turmas_page_data()
    assert len(turmas['alunos']) == 800
    assert len(turmas['aluno_vinculos']) == 800
    assert len(turmas['professor_vinculos']) == 200
    assert len(turmas['disciplina_vinculos']) == 200
    assert all(v['turma_id'] and v['aluno_id'] for v in turmas['aluno_vinculos'])
    assert len(list((Path(pasta) / 'uploads').glob('*.txt'))) == 1400
    with engine.connect() as db:
        assert not db.execute(text('PRAGMA foreign_key_check')).all()
        inconsistentes = db.scalar(text('''SELECT COUNT(*) FROM notas n
            JOIN alunos_turmas a ON a.aluno_id = n.aluno_id
            LEFT JOIN professores_turmas p ON p.professor_id = n.professor_id AND p.turma_id = a.turma_id
            LEFT JOIN professores_disciplinas d ON d.professor_id = n.professor_id AND d.disciplina_id = n.disciplina_id
            WHERE p.id IS NULL OR d.id IS NULL'''))
        assert inconsistentes == 0
    print('Carga validada: 1000 pessoas, todas as tabelas populadas, vínculos íntegros, 1400 arquivos e reexecução sem duplicatas.')
