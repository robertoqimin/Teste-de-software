from sqlalchemy import Integer, String, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UsuarioModel(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    senha: Mapped[str] = mapped_column(String(200), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)

    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="1")
    exigir_troca: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="0")
    versao_sessao: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    permissoes: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    professor = relationship("ProfessorModel", back_populates="usuario", uselist=False)
    aluno = relationship("AlunoModel", back_populates="usuario", uselist=False)
