from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class HorarioModel(Base):
    __tablename__ = 'horarios'
    __table_args__ = (
        UniqueConstraint('turma_disciplina_id', 'dia_semana', 'inicio', name='uq_horario_vinculo'),
        CheckConstraint('dia_semana >= 0 AND dia_semana <= 5', name='ck_horario_dia'),
        CheckConstraint('inicio < fim', name='ck_horario_intervalo'),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    turma_disciplina_id: Mapped[int] = mapped_column(ForeignKey('turmas_disciplinas.id'), nullable=False)
    dia_semana: Mapped[int] = mapped_column(Integer, nullable=False)
    inicio: Mapped[str] = mapped_column(String(5), nullable=False)
    fim: Mapped[str] = mapped_column(String(5), nullable=False)
    demonstracao: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
