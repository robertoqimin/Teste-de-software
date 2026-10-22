"""Models da aplicacao."""

from .aluno_model import AlunoModel
from .aluno_disciplina_model import AlunoDisciplinaModel
from .aluno_turma_model import AlunoTurmaModel
from .atividade_model import AtividadeModel
from .comunicado_model import ComunicadoModel
from .disciplina_model import DisciplinaModel
from .documento_model import DocumentoModel
from .nota_model import NotaModel
from .professor_model import ProfessorModel
from .professor_disciplina_model import ProfessorDisciplinaModel
from .professor_turma_model import ProfessorTurmaModel
from .solicitacao_documento_model import SolicitacaoDocumentoModel
from .turma_model import TurmaModel
from .turma_disciplina_model import TurmaDisciplinaModel
from .usuario_model import UsuarioModel

__all__ = [
    "UsuarioModel",
    "ProfessorModel",
    "ProfessorDisciplinaModel",
    "ProfessorTurmaModel",
    "SolicitacaoDocumentoModel",
    "AlunoModel",
    "AlunoDisciplinaModel",
    "AlunoTurmaModel",
    "AtividadeModel",
    "ComunicadoModel",
    "DisciplinaModel",
    "DocumentoModel",
    "NotaModel",
    "TurmaModel",
    "TurmaDisciplinaModel",
]

from .governanca_model import ConfiguracaoModel, AuditoriaModel
from .horario_model import HorarioModel
