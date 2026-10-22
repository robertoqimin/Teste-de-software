from datetime import datetime, timezone
from sqlalchemy import Integer, String, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class ConfiguracaoModel(Base):
    __tablename__ = "configuracoes"
    chave: Mapped[str] = mapped_column(String(80), primary_key=True)
    valor: Mapped[dict] = mapped_column(JSON, nullable=False)


class AuditoriaModel(Base):
    __tablename__ = "auditoria"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    email: Mapped[str] = mapped_column(String(120), nullable=False)
    acao: Mapped[str] = mapped_column(String(255), nullable=False)
    detalhes: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    data: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
