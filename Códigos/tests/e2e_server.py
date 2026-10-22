"""Servidor E2E: banco e uploads temporários, sem tocar no MySQL da aplicação."""
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

workspace = TemporaryDirectory(prefix="secretaria-spa-e2e-")
os.environ["DB_URL"] = "sqlite:///" + str(Path(workspace.name) / "test.db")
os.environ["UPLOAD_FOLDER"] = str(Path(workspace.name) / "uploads")
os.environ["SECRET_KEY"] = "e2e-isolated-secret"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app  # noqa: E402
from app.database import get_session  # noqa: E402
from app.models import (  # noqa: E402
    AlunoModel, AlunoTurmaModel, DisciplinaModel, ProfessorDisciplinaModel,
    ProfessorModel, ProfessorTurmaModel, TurmaDisciplinaModel, TurmaModel, UsuarioModel,
)
from werkzeug.security import generate_password_hash  # noqa: E402

app = create_app()
with get_session() as db:
    for role in ("admin", "aluno", "professor"):
        db.add(UsuarioModel(email=f"{role}@teste.local", senha=generate_password_hash("teste123"), tipo=role))
    db.flush()
    aluno = AlunoModel(usuario_id=2, nome="Aluno Teste", matricula="TESTE001", cpf="11111111111", status_matricula="Ativo", curso_serie="Ensino Médio")
    professor = ProfessorModel(usuario_id=3, nome="Professor Teste", cpf="22222222222", disciplina_principal="Matemática", regime_trabalho="40 horas semanais")
    disciplina = DisciplinaModel(nome="Matemática", codigo="MAT", carga_horaria=80)
    turma = TurmaModel(nome="Turma Teste", codigo="T1", ano_letivo=2026, turno="Matutino")
    db.add_all([aluno, professor, disciplina, turma])
    db.flush()
    db.add_all([
        AlunoTurmaModel(aluno_id=aluno.id, turma_id=turma.id),
        ProfessorTurmaModel(professor_id=professor.id, turma_id=turma.id),
        ProfessorDisciplinaModel(professor_id=professor.id, disciplina_id=disciplina.id),
        TurmaDisciplinaModel(turma_id=turma.id, disciplina_id=disciplina.id),
    ])
    db.commit()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("SPA_TEST_PORT", "5051")), debug=False)
