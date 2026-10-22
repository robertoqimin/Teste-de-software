"""Testes isolados de migração, autorização, revogação e recuperação."""
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

workspace = tempfile.TemporaryDirectory(prefix='secretaria-governanca-')
os.environ['DB_URL'] = 'sqlite:///' + str(Path(workspace.name) / 'test.db')
os.environ['SECRET_KEY'] = 'test-only-secret'
os.environ['UPLOAD_FOLDER'] = str(Path(workspace.name) / 'uploads')
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app
from app.database import Base, engine, get_session
from app.models import UsuarioModel, ConfiguracaoModel
from werkzeug.security import generate_password_hash


class GovernancaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.testing = True

    def setUp(self):
        with engine.begin() as connection:
            for table in reversed(Base.metadata.sorted_tables):
                connection.execute(table.delete())
        with get_session() as db:
            db.add(ConfiguracaoModel(chave='migracao_secretaria_v1', valor={}))
            for email, role in [('admin@test.local', 'admin'), ('secretaria@test.local', 'secretaria'), ('aluno@test.local', 'aluno')]:
                db.add(UsuarioModel(email=email, tipo=role, senha=generate_password_hash('teste1234')))
            db.commit()
        self.client = self.app.test_client()

    def login(self, client=None, email='admin@test.local'):
        response = (client or self.client).post('/login', json=dict(email=email, senha='teste1234'))
        self.assertEqual(response.status_code, 200)
        return response.json

    def test_legacy_schema_is_migrated(self):
        from sqlalchemy import text
        Base.metadata.drop_all(bind=engine)
        with engine.begin() as connection:
            connection.execute(text("CREATE TABLE usuarios (id INTEGER PRIMARY KEY, email VARCHAR(120) UNIQUE NOT NULL, senha VARCHAR(200) NOT NULL, tipo VARCHAR(20) NOT NULL)"))
            connection.execute(text("INSERT INTO usuarios (id, email, senha, tipo) VALUES (1, 'legado@test.local', :senha, 'ADMIN')"), {'senha': generate_password_hash('teste1234')})
        create_app()
        self.login(email='legado@test.local')
        self.assertEqual(self.client.get('/api/session').json['user']['role'], 'secretaria')
        self.assertEqual(self.client.get('/api/admin/dashboard').status_code, 200)

    def test_weekly_schedule_and_access(self):
        from app.models import TurmaModel, DisciplinaModel, HorarioModel, AlunoModel, AlunoTurmaModel
        with get_session() as db:
            turma = TurmaModel(nome='Turma A', codigo='A', ano_letivo=2026)
            outra = TurmaModel(nome='Turma B', codigo='B', ano_letivo=2026)
            disciplina = DisciplinaModel(nome='Matemática', codigo='MAT', carga_horaria=80)
            aluno = AlunoModel(usuario_id=3, nome='Aluno', matricula='A001')
            db.add_all([turma, outra, disciplina, aluno]); db.flush()
            turma_id, outra_id, disciplina_id = turma.id, outra.id, disciplina.id
            db.add(AlunoTurmaModel(aluno_id=aluno.id, turma_id=turma.id)); db.commit()
        self.login()
        payload = {'action': 'schedule', 'turma_id': turma_id, 'disciplina_id': disciplina_id, 'dias': ['0', '2'], 'inicio': '07:00', 'fim': '07:50'}
        self.assertEqual(self.client.post('/api/admin/turmas', data=payload).status_code, 403)
        self.login(email='secretaria@test.local')
        self.assertEqual(self.client.post('/api/admin/turmas', data={**payload, 'fim': '06:00'}).status_code, 400)
        self.assertEqual(self.client.post('/api/admin/turmas', data={**payload, 'dias': '7'}).status_code, 400)
        self.assertEqual(self.client.post('/api/admin/turmas', data=payload).status_code, 200)
        self.assertEqual(self.client.post('/api/admin/turmas', data={**payload, 'inicio': '07:30', 'fim': '08:00'}).status_code, 409)
        self.assertEqual(self.client.post('/api/admin/turmas', data={**payload, 'turma_id': outra_id}).status_code, 200)
        grade = self.client.get('/api/admin/turmas').json['horarios']
        horario_id = next(h['id'] for h in grade if h['turma_id'] == turma_id and h['dia_semana'] == 0)
        self.assertEqual(self.client.post('/api/admin/turmas', data={**payload, 'horario_id': horario_id, 'dias': '0', 'inicio': '07:50', 'fim': '08:40'}).status_code, 200)
        self.login(email='aluno@test.local')
        propria = self.client.get('/api/aluno').json['horarios']
        self.assertEqual(len(propria), 2)
        self.assertEqual({h['turma'] for h in propria}, {'Turma A'})
        self.assertEqual(self.client.post('/api/admin/turmas', data=payload).status_code, 403)
        self.login(email='secretaria@test.local')
        self.assertEqual(self.client.post('/api/admin/turmas', data={'action': 'remove_schedule', 'horario_id': horario_id}).status_code, 200)
        with get_session() as db:
            self.assertIsNone(db.get(HorarioModel, horario_id))

    def test_discipline_associations_are_complete(self):
        from app.models import ProfessorModel, ProfessorDisciplinaModel, DisciplinaModel
        password_hash = generate_password_hash('teste1234')
        with get_session() as db:
            disciplina = DisciplinaModel(nome='Teste', codigo='TEST', carga_horaria=40)
            db.add(disciplina); db.flush()
            for i in range(205):
                user = UsuarioModel(email=f'prof{i}@test.local', tipo='professor', senha=password_hash)
                db.add(user); db.flush()
                professor = ProfessorModel(usuario_id=user.id, nome=f'Professor {i}', cpf=f'999{i:08d}')
                db.add(professor); db.flush()
                db.add(ProfessorDisciplinaModel(professor_id=professor.id, disciplina_id=disciplina.id))
            db.commit()
        self.login(email='secretaria@test.local')
        data = self.client.get('/api/admin/disciplinas').json
        self.assertEqual(len(data['professores']), 205)
        self.assertEqual(len(data['professor_vinculos']), 205)
        self.assertEqual(len({v['professor_id'] for v in data['professor_vinculos']}), 205)
        self.assertTrue(all(v['disciplina_id'] for v in data['professor_vinculos']))

    def test_roles_are_separate(self):
        self.login(email='secretaria@test.local')
        self.assertEqual(self.client.get('/api/admin/dashboard').status_code, 200)
        self.assertEqual(self.client.get('/api/gestao/painel').status_code, 403)
        self.login()
        self.assertEqual(self.client.get('/api/gestao/painel').status_code, 200)
        self.assertEqual(self.client.get('/api/admin/dashboard').status_code, 403)

    def test_create_permissions_and_revocation(self):
        self.login()
        response = self.client.post('/api/gestao/usuarios', json=dict(email='nova@test.local', senha='teste1234', role='secretaria', permissoes={'academico': False}, exigir_troca=False))
        self.assertEqual(response.status_code, 201)
        other = self.app.test_client()
        self.login(other, 'nova@test.local')
        self.assertEqual(other.post('/api/admin/disciplinas', data={'nome': 'Teste', 'codigo': 'T'}).status_code, 403)
        self.assertEqual(other.post('/admin/disciplinas', data={'nome': 'Teste', 'codigo': 'T'}).status_code, 403)
        users = self.client.get('/api/gestao/painel').json['usuarios']
        user_id = next(u['id'] for u in users if u['email'] == 'nova@test.local')
        self.assertEqual(self.client.post(f'/api/gestao/usuarios/{user_id}', json={'ativo': False}).status_code, 200)
        self.assertEqual(other.get('/api/session').json, {'user': None})
        self.assertEqual(other.get('/api/admin/dashboard').status_code, 401)
        self.assertEqual(other.post('/login', json=dict(email='nova@test.local', senha='teste1234')).status_code, 403)

    def test_migration_is_once_and_seed_is_non_destructive(self):
        with get_session() as db:
            db.query(ConfiguracaoModel).delete()
            db.commit()
        create_app()
        with get_session() as db:
            self.assertEqual(db.query(UsuarioModel).filter_by(email='admin@test.local').one().tipo, 'secretaria')
            db.add(UsuarioModel(email='novo.admin@test.local', tipo='admin', senha=generate_password_hash('teste1234')))
            db.commit()
        from app.seed import run_seed
        run_seed('novo.admin@test.local', 'teste1234', 'admin')
        create_app()
        with get_session() as db:
            self.assertEqual(db.query(UsuarioModel).count(), 4)
            self.assertEqual(db.query(UsuarioModel).filter_by(email='novo.admin@test.local').one().tipo, 'admin')

    def test_backup_restore_and_failed_restore_preserves_database(self):
        self.login()
        backup = self.client.get('/api/gestao/backup')
        self.assertEqual(backup.status_code, 200)
        self.assertEqual(self.client.post('/api/gestao/usuarios', json=dict(email='nova@test.local', senha='teste1234', role='secretaria')).status_code, 201)
        response = self.client.post('/api/gestao/restaurar', data={'backup': (io.BytesIO(backup.data), 'backup.json'), 'confirmacao': 'RESTAURAR', 'senha': 'errada'})
        self.assertEqual(response.status_code, 403)
        response = self.client.post('/api/gestao/restaurar', data={'backup': (io.BytesIO(backup.data), 'backup.json'), 'confirmacao': 'RESTAURAR', 'senha': 'teste1234'})
        self.assertEqual(response.status_code, 200, response.json)
        self.assertIsNone(self.client.get('/api/session').json['user'])
        self.login()
        with get_session() as db:
            self.assertEqual(db.query(UsuarioModel).count(), 3)
        broken = json.loads(backup.data)
        broken['tabelas']['usuarios'][1]['email'] = broken['tabelas']['usuarios'][0]['email']
        response = self.client.post('/api/gestao/restaurar', data={'backup': (io.BytesIO(json.dumps(broken).encode()), 'backup.json'), 'confirmacao': 'RESTAURAR', 'senha': 'teste1234'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.client.get('/api/gestao/painel').status_code, 200)

    def test_forced_password_change_and_jwt_revocation(self):
        token = self.login(email='secretaria@test.local')['token']
        self.login()
        self.assertEqual(self.client.post('/api/gestao/usuarios/2', json={'exigir_troca': True}).status_code, 200)
        other = self.app.test_client()
        self.login(other, 'secretaria@test.local')
        self.assertTrue(other.get('/api/session').json['user']['exigir_troca'])
        self.assertEqual(other.get('/api/admin/dashboard').status_code, 403)
        self.assertEqual(other.post('/api/senha', json={'senha_atual': 'teste1234', 'nova_senha': 'novasenha123'}).status_code, 200)
        self.assertEqual(other.get('/api/admin/dashboard').status_code, 200)
        self.assertEqual(other.get('/professor/teste', headers={'Authorization': 'Bearer ' + token}).status_code, 401)

    def test_grade_deadline(self):
        self.login()
        self.assertEqual(self.client.post('/api/gestao/configuracoes', json=dict(ano_letivo=2026, periodos=4, media_aprovacao=6, prazo_notas='2000-01-01')).status_code, 200)
        with get_session() as db:
            db.add(UsuarioModel(email='professor@test.local', tipo='professor', senha=generate_password_hash('teste1234')))
            db.commit()
        self.login(email='professor@test.local')
        response = self.client.post('/api/professor/notas/salvar', data={})
        self.assertEqual(response.status_code, 403)
        self.assertIn('prazo', response.json['erro'])

    def test_seed_default_admin(self):
        from app.seed import run_seed
        with self.assertRaises(ValueError):
            run_seed(senha='123')
        run_seed(senha='novaSenha123')
        run_seed(senha='outraSenha123')
        with get_session() as db:
            user = db.query(UsuarioModel).filter_by(email='gestor@escola.com').one()
            self.assertEqual(user.tipo, 'admin')
            from werkzeug.security import check_password_hash
            self.assertTrue(check_password_hash(user.senha, 'novaSenha123'))
            self.assertIsNone(db.query(UsuarioModel).filter_by(email='admin@admin.com').first())

    def test_activity_delivery_authorization_and_history(self):
        from app.models import AlunoModel, ProfessorModel, TurmaModel, DisciplinaModel, AlunoTurmaModel, TurmaDisciplinaModel, AtividadeModel, DocumentoModel
        with get_session() as db:
            aluno_user = db.query(UsuarioModel).filter_by(tipo='aluno').one()
            teacher_user = UsuarioModel(email='prof@test.local', tipo='professor', senha=generate_password_hash('teste1234'))
            other_user = UsuarioModel(email='outro@test.local', tipo='aluno', senha=generate_password_hash('teste1234'))
            db.add_all([teacher_user, other_user]); db.flush()
            aluno = AlunoModel(usuario_id=aluno_user.id, nome='Aluno', matricula='ENT1')
            outro = AlunoModel(usuario_id=other_user.id, nome='Outro', matricula='ENT2')
            professor = ProfessorModel(usuario_id=teacher_user.id, nome='Professor', cpf='12345678901')
            turma = TurmaModel(nome='Turma', codigo='ENT', ano_letivo=2026)
            disciplina = DisciplinaModel(nome='Disciplina', codigo='ENT', carga_horaria=80)
            db.add_all([aluno, outro, professor, turma, disciplina]); db.flush()
            atividade = AtividadeModel(titulo='Entrega', professor_id=professor.id, turma_id=turma.id, disciplina_id=disciplina.id)
            db.add_all([atividade, AlunoTurmaModel(aluno_id=aluno.id, turma_id=turma.id), TurmaDisciplinaModel(turma_id=turma.id, disciplina_id=disciplina.id)])
            db.commit()
            atividade_id, disciplina_id = atividade.id, disciplina.id
        url = f'/api/aluno/atividades/{atividade_id}/enviar'
        self.login(email='outro@test.local')
        self.assertEqual(self.client.post(url, data={'arquivo': (io.BytesIO(b'outro'), 'resposta.txt')}).status_code, 404)
        self.login(email='aluno@test.local')
        self.assertEqual(self.client.post(url).status_code, 400)
        self.assertEqual(self.client.post(url, data={'arquivo': (io.BytesIO(b'resposta'), 'resposta.txt')}).status_code, 201)
        self.assertEqual(self.client.post(url, data={'arquivo': (io.BytesIO(b'nova'), 'nova.txt')}).status_code, 201)
        detail = self.client.get(f'/api/aluno/disciplinas/{disciplina_id}').json
        self.assertEqual(len(detail['atividades'][0]['entregas']), 2)
        filename = detail['atividades'][0]['entregas'][0]['arquivo']
        with self.client.get('/arquivos/download/' + filename) as response:
            self.assertEqual(response.status_code, 200)
        self.login(email='outro@test.local')
        self.assertEqual(self.client.get('/arquivos/download/' + filename).status_code, 404)
        self.login(email='prof@test.local')
        with self.client.get('/arquivos/download/' + filename) as response:
            self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.post(url, data={'arquivo': (io.BytesIO(b'x'), 'x.txt')}).status_code, 403)
        with get_session() as db:
            docs = db.query(DocumentoModel).filter_by(atividade_id=atividade_id).all()
            self.assertEqual(len(docs), 2)
            self.assertTrue(all(d.professor_id is not None for d in docs))

    def test_paginated_users_and_academic_records(self):
        from app.models import AlunoModel, ProfessorModel
        with get_session() as db:
            for n in range(27):
                user = UsuarioModel(email=f'pessoa{n:02}@test.local', tipo='aluno' if n < 23 else 'professor', senha='unused')
                db.add(user)
                db.flush()
                if n < 23:
                    db.add(AlunoModel(usuario_id=user.id, nome=f'Aluno {n}', matricula=f'M{n}'))
                else:
                    db.add(ProfessorModel(usuario_id=user.id, nome=f'Professor {n}', cpf=f'{n:011}'))
            db.commit()
        self.login()
        first = self.client.get('/api/gestao/painel').json
        second = self.client.get('/api/gestao/painel?page=2').json
        self.assertEqual(first['pagination']['total'], 30)
        self.assertEqual(len(first['usuarios']), 20)
        self.assertEqual(len(second['usuarios']), 10)
        self.assertFalse({u['id'] for u in first['usuarios']} & {u['id'] for u in second['usuarios']})
        filtered = self.client.get('/api/gestao/painel?search=pessoa26&role=professor').json
        self.assertEqual(filtered['pagination']['total'], 1)
        self.login(email='secretaria@test.local')
        first = self.client.get('/api/admin/registros').json
        second = self.client.get('/api/admin/registros?page=2').json
        self.assertEqual(len(first['alunos']), 20)
        self.assertEqual(len(first['professores']), 0)
        self.assertEqual(len(second['alunos']), 3)
        self.assertEqual(len(second['professores']), 4)
        self.assertFalse({u['id'] for u in first['alunos']} & {u['id'] for u in second['alunos']})
        filtered = self.client.get('/api/admin/registros?search=pessoa26&type=professor').json
        self.assertEqual(filtered['pagination']['total'], 1)
        self.assertEqual(len(filtered['professores']), 1)
        empty = self.client.get('/api/admin/registros?search=inexistente&page=99').json
        self.assertEqual(empty['pagination']['page'], 1)
        self.assertEqual(empty['pagination']['total'], 0)
        exported = self.client.get('/api/admin/registros?export=1').json
        self.assertEqual(len(exported['alunos']) + len(exported['professores']), 27)
        bounded = self.client.get('/api/admin/registros?page=999&page_size=10').json
        self.assertEqual(bounded['pagination']['page'], 3)
        self.assertEqual(len(bounded['alunos']) + len(bounded['professores']), 7)

    def test_validation_audit_and_no_self_lockout(self):
        self.login()
        self.assertEqual(self.client.post('/api/gestao/usuarios/1', json={'ativo': False}).status_code, 400)
        self.assertEqual(self.client.post('/api/gestao/usuarios', json=dict(email='x@test.local', senha='123', role='admin')).status_code, 400)
        self.assertEqual(self.client.post('/api/gestao/configuracoes', json=dict(ano_letivo=2026, periodos=4, media_aprovacao=6, prazo_notas='2026-12-01')).status_code, 200)
        data = self.client.get('/api/gestao/painel').json
        self.assertEqual(data['configuracoes']['periodos'], 4)
        self.assertTrue(any(a['acao'] == 'Configurações acadêmicas alteradas' for a in data['auditoria']))
        self.assertNotIn('teste1234', json.dumps(data))
        self.assertEqual(self.client.get('/api/gestao/relatorio.csv').status_code, 200)


if __name__ == '__main__':
    unittest.main()
