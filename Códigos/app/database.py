from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

from config import Config

engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_session():
    return SessionLocal()


def init_db():
    Base.metadata.create_all(bind=engine)
    _ensure_schema_updates()
    # Executada uma única vez: contas antigas continuam na secretaria.
    with engine.begin() as connection:
        migrated = connection.execute(text("SELECT chave FROM configuracoes WHERE chave = 'migracao_secretaria_v1'")).first()
        if not migrated:
            connection.execute(text("UPDATE usuarios SET tipo = 'secretaria' WHERE LOWER(tipo) = 'admin'"))
            connection.execute(text("INSERT INTO configuracoes (chave, valor) VALUES ('migracao_secretaria_v1', '{}')"))


def _ensure_schema_updates():
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    if "usuarios" in table_names:
        _add_missing_columns(inspector, "usuarios", {
            "exigir_troca": "BOOLEAN NOT NULL DEFAULT 0",
            "ativo": "BOOLEAN NOT NULL DEFAULT 1",
            "versao_sessao": "INTEGER NOT NULL DEFAULT 0",
            "permissoes": "JSON NULL",
        })

    if "alunos" in table_names:
        _add_missing_columns(
            inspector,
            "alunos",
            {
                "cpf": "VARCHAR(14) NULL",
                "curso_serie": "VARCHAR(80) NULL",
                "status_matricula": "VARCHAR(20) NULL",
                "foto_perfil": "VARCHAR(255) NULL",
            },
        )

    if "professores" in table_names:
        _add_missing_columns(
            inspector,
            "professores",
            {
                "disciplina_principal": "VARCHAR(80) NULL",
                "formacao_academica": "VARCHAR(120) NULL",
                "regime_trabalho": "VARCHAR(50) NULL",
                "foto_perfil": "VARCHAR(255) NULL",
                "data_admissao": "DATE NULL",
            },
        )

    if "documentos" in table_names:
        _add_missing_columns(inspector, "documentos", {"atividade_id": "INTEGER NULL"})
        _make_nullable_if_needed(inspector, "documentos", "aluno_id", "INTEGER NULL")
        _make_nullable_if_needed(inspector, "documentos", "professor_id", "INTEGER NULL")

    if "solicitacoes_documentos" in table_names:
        _add_missing_columns(
            inspector,
            "solicitacoes_documentos",
            {
                "professor_id": "INTEGER NULL",
            },
        )
        _make_nullable_if_needed(
            inspector,
            "solicitacoes_documentos",
            "aluno_id",
            "INTEGER NULL",
        )

    if "atividades" in table_names:
        _add_missing_columns(
            inspector,
            "atividades",
            {
                "caminho_arquivo": "VARCHAR(255) NULL",
                "tipo": "VARCHAR(20) NOT NULL DEFAULT 'atividade'",
            },
        )


def _add_missing_columns(inspector, table_name, columns_to_add):
    columns = {column["name"] for column in inspector.get_columns(table_name)}
    missing_columns = [
        (column_name, column_definition)
        for column_name, column_definition in columns_to_add.items()
        if column_name not in columns
    ]
    if not missing_columns:
        return

    # Atualiza bancos antigos sem exigir ferramenta de migracao neste projeto.
    with engine.begin() as connection:
        for column_name, column_definition in missing_columns:
            connection.execute(
                text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")
            )


def _make_nullable_if_needed(inspector, table_name, column_name, column_definition):
    columns = {column["name"]: column for column in inspector.get_columns(table_name)}
    column = columns.get(column_name)
    if not column or column.get("nullable"):
        return

    if engine.dialect.name != "mysql":
        return

    with engine.begin() as connection:
        connection.execute(
            text(f"ALTER TABLE {table_name} MODIFY COLUMN {column_name} {column_definition}")
        )
