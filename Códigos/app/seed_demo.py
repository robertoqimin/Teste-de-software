"""Carga fictícia completa e idempotente: 800 alunos e 200 professores."""
import json
import random
import secrets
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

from sqlalchemy import func, select
from werkzeug.security import generate_password_hash

from app import create_app
from app.database import Base, engine, get_session
from app.models import (
    HorarioModel, AlunoModel, AlunoDisciplinaModel, AlunoTurmaModel, AtividadeModel,
    AuditoriaModel, ComunicadoModel, ConfiguracaoModel, DisciplinaModel,
    DocumentoModel, NotaModel, ProfessorModel, ProfessorDisciplinaModel,
    ProfessorTurmaModel, SolicitacaoDocumentoModel, TurmaDisciplinaModel,
    TurmaModel, UsuarioModel,
)

MARCADOR = 'carga_demo_v1'
DISCIPLINAS = ['Matemática', 'Língua Portuguesa', 'História', 'Geografia',
               'Biologia', 'Física', 'Química', 'Inglês', 'Artes', 'Educação Física']
NOMES = ['Ana', 'Bruno', 'Carla', 'Daniel', 'Elisa', 'Felipe', 'Gabriela', 'Hugo',
         'Isabela', 'João', 'Karen', 'Lucas', 'Mariana', 'Nicolas', 'Olívia',
         'Paulo', 'Rafaela', 'Samuel', 'Talita', 'Vitor']
SOBRENOMES = ['Silva', 'Santos', 'Oliveira', 'Souza', 'Lima', 'Pereira', 'Costa',
              'Almeida', 'Ferreira', 'Rodrigues', 'Gomes', 'Ribeiro', 'Martins',
              'Barbosa', 'Rocha', 'Dias', 'Mendes', 'Cardoso', 'Teixeira', 'Araújo']


def contagens():
    with engine.connect() as connection:
        return {table.name: connection.scalar(select(func.count()).select_from(table))
                for table in Base.metadata.sorted_tables}


def popular():
    app = create_app()
    rng = random.Random(2026)
    agora = datetime.now(timezone.utc).replace(tzinfo=None)
    ano = 2026
    arquivos_criados = []
    pasta = Path(app.config['UPLOAD_FOLDER']).resolve()
    senha = secrets.token_urlsafe(15)
    senha_hash = generate_password_hash(senha)

    def nome(indice):
        return f'{NOMES[indice % 20]} {SOBRENOMES[(indice // 20) % 20]} Demo {indice + 1:04d}'

    def arquivo(nome_arquivo, conteudo):
        destino = pasta / nome_arquivo
        # Arquivos existentes também são preservados em uma reexecução.
        with destino.open('x', encoding='utf-8') as output:
            arquivos_criados.append(destino)
            output.write('DADOS FICTÍCIOS PARA DEMONSTRAÇÃO\n\n' + conteudo)
        return nome_arquivo

    with get_session() as db:
        if db.get(ConfiguracaoModel, MARCADOR):
            print('Carga já executada; dados preservados.')
            print(json.dumps(contagens(), ensure_ascii=False, indent=2))
            return
        try:
            pasta.mkdir(parents=True, exist_ok=True)
            disciplinas = [DisciplinaModel(nome=n, codigo=f'DEMO-D{i+1:02d}', carga_horaria=80 if i < 7 else 40)
                           for i, n in enumerate(DISCIPLINAS)]
            turmas = [TurmaModel(nome=f'{i % 3 + 1}º ano EM - Demo {i+1:02d}', codigo=f'DEMO-T{i+1:02d}',
                                 ano_letivo=ano, turno='Matutino' if i < 10 else 'Vespertino')
                      for i in range(20)]
            db.add_all(disciplinas + turmas)
            db.flush()
            professores = []
            alunos = []
            for role, quantidade, pessoas in [('professor', 200, professores), ('aluno', 800, alunos)]:
                for i in range(quantidade):
                    usuario = UsuarioModel(email=f'{role}{i+1:04d}@demo.invalid', senha=senha_hash,
                                           tipo=role, ativo=True, exigir_troca=False, permissoes={})
                    db.add(usuario)
                    db.flush()
                    if role == 'professor':
                        pessoa = ProfessorModel(usuario_id=usuario.id, nome=nome(800 + i),
                            cpf=f'900{i+1:08d}', telefone=None,
                            disciplina_principal=DISCIPLINAS[i % 10],
                            formacao_academica=f'Licenciatura em {DISCIPLINAS[i % 10]}',
                            regime_trabalho='40 horas semanais', data_admissao=date(2020 + i % 6, 2, 1))
                    else:
                        pessoa = AlunoModel(usuario_id=usuario.id, nome=nome(i), cpf=f'800{i+1:08d}',
                            matricula=f'DEMO-{ano}-{i+1:04d}', curso_serie=f'{(i // 40) % 3 + 1}º ano do Ensino Médio',
                            status_matricula='Pendente' if i % 20 == 0 else 'Ativo',
                            data_nascimento=date(2009 - ((i // 40) % 3), i % 12 + 1, i % 28 + 1))
                    db.add(pessoa)
                    pessoas.append(pessoa)
            db.flush()

            for ti, turma in enumerate(turmas):
                for di, disciplina in enumerate(disciplinas):
                    professor = professores[ti * 10 + di]
                    vinculo = TurmaDisciplinaModel(turma_id=turma.id, disciplina_id=disciplina.id)
                    db.add_all([
                        vinculo,
                        ProfessorDisciplinaModel(professor_id=professor.id, disciplina_id=disciplina.id),
                        ProfessorTurmaModel(professor_id=professor.id, turma_id=turma.id),
                    ])
                    db.flush()
                    inicio = (7 * 60 if turma.turno == 'Matutino' else 13 * 60) + (di % 2) * 50
                    fim = inicio + 50
                    db.add(HorarioModel(turma_disciplina_id=vinculo.id, dia_semana=di // 2,
                        inicio=f'{inicio // 60:02d}:{inicio % 60:02d}', fim=f'{fim // 60:02d}:{fim % 60:02d}', demonstracao=True))
                    for numero in (1, 2):
                        caminho = arquivo(f'demo_atividade_t{ti+1:02d}_d{di+1:02d}_{numero}.txt',
                                          f'Atividade {numero}: {disciplina.nome}\nResolva os exercícios e entregue ao professor.\n')
                        db.add(AtividadeModel(professor_id=professor.id, turma_id=turma.id,
                            disciplina_id=disciplina.id, titulo=f'Lista {numero} — {disciplina.nome}',
                            descricao='Exercícios de revisão e aplicação dos conteúdos estudados. Material fictício.',
                            data_entrega=(date(ano, 11, 1) + timedelta(days=numero * 7)).isoformat(), caminho_arquivo=caminho))

            for i, aluno in enumerate(alunos):
                ti = i // 40
                turma = turmas[ti]
                db.add(AlunoTurmaModel(aluno_id=aluno.id, turma_id=turma.id))
                for di, disciplina in enumerate(disciplinas):
                    db.add_all([
                        AlunoDisciplinaModel(aluno_id=aluno.id, disciplina_id=disciplina.id),
                        NotaModel(aluno_id=aluno.id, disciplina_id=disciplina.id,
                            professor_id=professores[ti * 10 + di].id,
                            nota=Decimal(rng.randrange(30, 101)) / 10,
                            observacao='Avaliação fictícia para demonstração.'),
                    ])

            for role, pessoas in [('aluno', alunos), ('professor', professores)]:
                for i, pessoa in enumerate(pessoas):
                    disciplina = disciplinas[i % 10] if role == 'professor' else disciplinas[0]
                    alvo = {'aluno_id': pessoa.id} if role == 'aluno' else {'professor_id': pessoa.id}
                    caminho = arquivo(f'demo_documento_{role}_{i+1:04d}.txt',
                                      f'Comprovante fictício de {pessoa.nome}.\nSem validade oficial.\n')
                    documento = DocumentoModel(**alvo, disciplina_id=disciplina.id,
                        titulo='Comprovante fictício de cadastro', caminho_arquivo=caminho)
                    db.add(documento)
                    db.flush()
                    concluida = i % 3 != 0
                    db.add(SolicitacaoDocumentoModel(**alvo,
                        titulo='Atualização documental — demonstração',
                        mensagem='Enviar comprovante fictício para atualização do cadastro.',
                        status='enviado' if concluida else 'pendente',
                        documento_id=documento.id if concluida else None,
                        completed_at=agora if concluida else None))

            for i in range(12):
                db.add(ComunicadoModel(titulo=f'Comunicado Demo {i+1:02d}',
                    destinatario=['Todos', 'Alunos', 'Professores'][i % 3],
                    mensagem=['Calendário de avaliações disponível na secretaria.',
                              'Reunião pedagógica para acompanhamento das turmas.',
                              'Atualização de documentos cadastrais.'][i % 3] + ' Conteúdo fictício.',
                    criado_por='Carga de demonstração'))
            if not db.get(ConfiguracaoModel, 'academico'):
                db.add(ConfiguracaoModel(chave='academico', valor={
                    'ano_letivo': ano, 'periodos': 4, 'media_aprovacao': 6, 'prazo_notas': ''}))
            db.add(ConfiguracaoModel(chave=MARCADOR, valor={'alunos': 800, 'professores': 200, 'data': agora.isoformat()}))
            db.add(AuditoriaModel(email='carga-demo@demo.invalid', acao='População fictícia do banco',
                detalhes={'alunos': 800, 'professores': 200, 'turmas': 20, 'disciplinas': 10}))
            db.flush()
            for table in Base.metadata.sorted_tables:
                if not db.scalar(select(func.count()).select_from(table)):
                    raise RuntimeError(f'Tabela sem dados: {table.name}')
            db.commit()
        except BaseException:
            db.rollback()
            for caminho in arquivos_criados:
                caminho.unlink(missing_ok=True)
            raise
    print(json.dumps(contagens(), ensure_ascii=False, indent=2))
    print('Criados: 800 alunos e 200 professores (80:20).')
    print('Login de exemplo: aluno0001@demo.invalid / professor0001@demo.invalid')
    print(f'Senha das contas fictícias: {senha}')


if __name__ == '__main__':
    popular()
