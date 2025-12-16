# app/models/models.py

from datetime import datetime, date, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional, List

from sqlalchemy import Column, Numeric
from sqlmodel import SQLModel, Field, Relationship


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


# =========================
# ENUMS DE DOMÍNIO (estáveis)
# =========================


class UsuarioTipo(str, Enum):
    BB = "bb"
    NPBB = "npbb"
    AGENCIA = "agencia"


class Usuario(SQLModel, table=True):
    __tablename__ = "usuario"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(max_length=100, unique=True)
    matricula: Optional[str] = Field(default=None, max_length=20, unique=True)
    password_hash: str = Field(max_length=255)

    tipo_usuario: UsuarioTipo

    funcionario_id: Optional[int] = Field(default=None, foreign_key="funcionario.id")
    agencia_id: Optional[int] = Field(default=None, foreign_key="agencia.id")

    ativo: bool = Field(default=True)

    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(default_factory=now_utc)

    funcionario: Optional["Funcionario"] = Relationship(back_populates="usuario")
    agencia: Optional["Agencia"] = Relationship(back_populates="usuarios")


class PasswordResetToken(SQLModel, table=True):
    __tablename__ = "password_reset_token"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id", index=True)
    token_hash: str = Field(max_length=64, unique=True, index=True)

    created_at: datetime = Field(default_factory=now_utc)
    sent_at: datetime = Field(default_factory=now_utc)
    expires_at: datetime
    used_at: Optional[datetime] = None


class StatusEvento(str, Enum):
    PREVISTO = "Previsto"
    REALIZADO = "Realizado"
    CANCELADO = "Cancelado"
    EM_ANDAMENTO = "Em andamento"


class TipoInvestimento(str, Enum):
    PATROCINIO = "Patrocínio"
    PROMOCAO = "Promoção"


class TipoPergunta(str, Enum):
    ABERTA_TEXTO_SIMPLES = "aberta_texto_simples"
    ABERTA_TEXTO_AREA = "aberta_texto_area"
    OBJETIVA_UNICA = "objetiva_unica"
    OBJETIVA_MULTIPLA = "objetiva_multipla"
    DATA = "data"
    AVALIACAO = "avaliacao"
    NUMERICA = "numerica"


# =========================
# TABELAS BÁSICAS
# =========================


class Agencia(SQLModel, table=True):
    __tablename__ = "agencia"

    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(max_length=100)
    dominio: str = Field(max_length=100, unique=True)
    lote: int
    created_at: datetime = Field(default_factory=now_utc)
    logo_url: Optional[str] = Field(default=None, max_length=500)

    eventos: List["Evento"] = Relationship(back_populates="agencia")
    usuarios: List["Usuario"] = Relationship(back_populates="agencia")


class Diretoria(SQLModel, table=True):
    __tablename__ = "diretoria"

    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(max_length=100, unique=True)
    created_at: datetime = Field(default_factory=now_utc)

    funcionarios: List["Funcionario"] = Relationship(back_populates="diretoria")
    eventos: List["Evento"] = Relationship(back_populates="diretoria")
    cotas: List["CotaCortesia"] = Relationship(back_populates="diretoria")


class Funcionario(SQLModel, table=True):
    __tablename__ = "funcionario"

    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(max_length=100)
    chave_c: str = Field(max_length=20, unique=True)
    diretoria_id: int = Field(foreign_key="diretoria.id")
    email: str = Field(max_length=60, unique=True)
    telefone: Optional[str] = Field(default=None, max_length=25)
    created_at: datetime = Field(default_factory=now_utc)

    diretoria: Optional[Diretoria] = Relationship(back_populates="funcionarios")
    eventos_gestor: List["Evento"] = Relationship(back_populates="gestor")
    convites_feitos: List["Convite"] = Relationship(back_populates="funcionario_convidador")
    convidados_associados: List["Convidado"] = Relationship(back_populates="funcionario_associado")

    usuario: Optional["Usuario"] = Relationship(back_populates="funcionario")



# =========================
# EVENTO / TIPO / SUBTIPO
# =========================


class TipoEvento(SQLModel, table=True):
    __tablename__ = "tipo_evento"

    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(max_length=50, unique=True)

    subtipos: List["SubtipoEvento"] = Relationship(back_populates="tipo")
    eventos: List["Evento"] = Relationship(back_populates="tipo")


class SubtipoEvento(SQLModel, table=True):
    __tablename__ = "subtipo_evento"

    id: Optional[int] = Field(default=None, primary_key=True)
    tipo_id: int = Field(foreign_key="tipo_evento.id")
    nome: str = Field(max_length=80)

    tipo: Optional[TipoEvento] = Relationship(back_populates="subtipos")
    eventos: List["Evento"] = Relationship(back_populates="subtipo")


class Evento(SQLModel, table=True):
    __tablename__ = "evento"

    id: Optional[int] = Field(default=None, primary_key=True)
    thumbnail: Optional[str] = Field(default=None, max_length=500)
    # No banco é ENUM "divisao", aqui mantemos como str para flexibilidade futura
    divisao_demandante: Optional[str] = Field(default=None, max_length=100)
    qr_code_url: Optional[str] = Field(default=None, max_length=500)

    nome: str = Field(max_length=100)
    descricao: str = Field(max_length=240)

    data_inicio_prevista: Optional[date] = None
    data_inicio_realizada: Optional[date] = None
    data_fim_prevista: Optional[date] = None
    data_fim_realizada: Optional[date] = None

    publico_projetado: Optional[int] = None
    publico_realizado: Optional[int] = None

    concorrencia: bool = Field(default=False)
    cidade: str = Field(max_length=40)
    estado: str = Field(max_length=40)

    agencia_id: int = Field(foreign_key="agencia.id")
    diretoria_id: Optional[int] = Field(default=None, foreign_key="diretoria.id")
    gestor_id: Optional[int] = Field(default=None, foreign_key="funcionario.id")

    tipo_id: int = Field(foreign_key="tipo_evento.id")
    subtipo_id: Optional[int] = Field(default=None, foreign_key="subtipo_evento.id")

    status: StatusEvento

    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(default_factory=now_utc)

    agencia: Optional[Agencia] = Relationship(back_populates="eventos")
    diretoria: Optional[Diretoria] = Relationship(back_populates="eventos")
    gestor: Optional[Funcionario] = Relationship(back_populates="eventos_gestor")
    tipo: Optional[TipoEvento] = Relationship(back_populates="eventos")
    subtipo: Optional[SubtipoEvento] = Relationship(back_populates="eventos")

    territorios: List["EventoTerritorio"] = Relationship(back_populates="evento")
    tags: List["EventoTag"] = Relationship(back_populates="evento")
    ativacoes: List["Ativacao"] = Relationship(back_populates="evento")
    cotas: List["CotaCortesia"] = Relationship(back_populates="evento")
    paginas_questionario: List["QuestionarioPagina"] = Relationship(back_populates="evento")
    respostas_questionario: List["QuestionarioResposta"] = Relationship(back_populates="evento")


# =========================
# TERRITÓRIOS / TAGS
# =========================


class Territorio(SQLModel, table=True):
    __tablename__ = "territorio"

    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(max_length=80, unique=True)

    eventos: List["EventoTerritorio"] = Relationship(back_populates="territorio")


class EventoTerritorio(SQLModel, table=True):
    __tablename__ = "evento_territorio"

    id: Optional[int] = Field(default=None, primary_key=True)
    evento_id: int = Field(foreign_key="evento.id")
    territorio_id: int = Field(foreign_key="territorio.id")

    evento: Optional[Evento] = Relationship(back_populates="territorios")
    territorio: Optional[Territorio] = Relationship(back_populates="eventos")


class Tag(SQLModel, table=True):
    __tablename__ = "tag"

    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(max_length=80, unique=True)

    eventos: List["EventoTag"] = Relationship(back_populates="tag")


class EventoTag(SQLModel, table=True):
    __tablename__ = "evento_tag"

    id: Optional[int] = Field(default=None, primary_key=True)
    evento_id: int = Field(foreign_key="evento.id")
    tag_id: int = Field(foreign_key="tag.id")

    evento: Optional[Evento] = Relationship(back_populates="tags")
    tag: Optional[Tag] = Relationship(back_populates="eventos")


# =========================
# LEAD
# =========================


class Lead(SQLModel, table=True):
    __tablename__ = "lead"

    id: Optional[int] = Field(default=None, primary_key=True)
    id_salesforce: Optional[str] = Field(default=None, max_length=200, unique=True)

    nome: str = Field(max_length=100)
    sobrenome: str = Field(max_length=100)
    email: Optional[str] = Field(default=None, max_length=100)
    telefone: Optional[str] = Field(default=None, max_length=100)

    cpf: str = Field(max_length=11, unique=True)
    data_nascimento: date
    data_criacao: datetime = Field(default_factory=now_utc)

    ativacoes: List["AtivacaoLead"] = Relationship(back_populates="lead")
    cupons: List["Cupom"] = Relationship(back_populates="lead")
    respostas_questionario: List["QuestionarioResposta"] = Relationship(back_populates="lead")


# =========================
# ATIVAÇÃO / GAMIFICAÇÃO / TERMO / INVESTIMENTO / RELAÇÃO LEAD
# =========================


class Ativacao(SQLModel, table=True):
    __tablename__ = "ativacao"

    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(max_length=100)
    descricao: str = Field(max_length=200)
    evento_id: int = Field(foreign_key="evento.id")

    valor: Decimal = Field(sa_column=Column(Numeric(12, 2)))

    mensagem_qrcode: Optional[str] = Field(default=None, max_length=240)

    redireciona_pesquisa: bool = Field(default=False)
    checkin_unico: bool = Field(default=False)
    termo_uso: bool = Field(default=False)
    gera_cupom: bool = Field(default=False)

    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(default_factory=now_utc)

    evento: Optional[Evento] = Relationship(back_populates="ativacoes")
    gamificacao: Optional["Gamificacao"] = Relationship(back_populates="ativacao")
    termo_uso_obj: Optional["TermoUsoAtivacao"] = Relationship(back_populates="ativacao")
    investimentos: List["Investimento"] = Relationship(back_populates="ativacao")
    ativacao_leads: List["AtivacaoLead"] = Relationship(back_populates="ativacao")
    cupons: List["Cupom"] = Relationship(back_populates="ativacao")
    respostas_questionario: List["QuestionarioResposta"] = Relationship(back_populates="ativacao")


class Gamificacao(SQLModel, table=True):
    __tablename__ = "gamificacao"

    id: Optional[int] = Field(default=None, primary_key=True)
    ativacao_id: int = Field(foreign_key="ativacao.id", unique=True)

    nome: str = Field(max_length=150)
    descricao: str = Field(max_length=500)
    premio: Optional[str] = Field(default=None, max_length=200)
    titulo_feedback: Optional[str] = Field(default=None, max_length=200)
    texto_feedback: Optional[str] = Field(default=None, max_length=500)

    ativacao: Optional[Ativacao] = Relationship(back_populates="gamificacao")


class TermoUsoAtivacao(SQLModel, table=True):
    __tablename__ = "termo_uso_ativacao"

    id: Optional[int] = Field(default=None, primary_key=True)
    ativacao_id: int = Field(foreign_key="ativacao.id", unique=True)

    titulo: Optional[str] = Field(default=None, max_length=200)
    texto: str
    obrigatorio: bool = Field(default=True)

    ativacao: Optional[Ativacao] = Relationship(back_populates="termo_uso_obj")


class Investimento(SQLModel, table=True):
    __tablename__ = "investimento"

    id: Optional[int] = Field(default=None, primary_key=True)
    ativacao_id: int = Field(foreign_key="ativacao.id")

    tipo: TipoInvestimento
    descricao: str = Field(max_length=200)
    valor: Decimal = Field(sa_column=Column(Numeric(12, 2)))

    ativacao: Optional[Ativacao] = Relationship(back_populates="investimentos")


class AtivacaoLead(SQLModel, table=True):
    __tablename__ = "ativacao_lead"

    id: Optional[int] = Field(default=None, primary_key=True)
    ativacao_id: int = Field(foreign_key="ativacao.id")
    lead_id: int = Field(foreign_key="lead.id")

    ativacao: Optional[Ativacao] = Relationship(back_populates="ativacao_leads")
    lead: Optional[Lead] = Relationship(back_populates="ativacoes")


class Cupom(SQLModel, table=True):
    __tablename__ = "cupom"

    id: Optional[int] = Field(default=None, primary_key=True)
    ativacao_id: int = Field(foreign_key="ativacao.id")
    codigo: str = Field(max_length=50, unique=True)
    descricao: Optional[str] = Field(default=None, max_length=200)

    data_criacao: datetime = Field(default_factory=now_utc)
    data_validade: Optional[date] = None
    usado: bool = Field(default=False)
    usado_em: Optional[datetime] = None

    lead_id: Optional[int] = Field(default=None, foreign_key="lead.id")

    ativacao: Optional[Ativacao] = Relationship(back_populates="cupons")
    lead: Optional[Lead] = Relationship(back_populates="cupons")


# =========================
# COTAS / CONVIDADOS / CONVITES
# =========================


class CotaCortesia(SQLModel, table=True):
    __tablename__ = "cota_cortesia"

    id: Optional[int] = Field(default=None, primary_key=True)
    evento_id: int = Field(foreign_key="evento.id")
    diretoria_id: int = Field(foreign_key="diretoria.id")

    quantidade: int

    evento: Optional[Evento] = Relationship(back_populates="cotas")
    diretoria: Optional[Diretoria] = Relationship(back_populates="cotas")
    convites: List["Convite"] = Relationship(back_populates="cota")


class Convidado(SQLModel, table=True):
    __tablename__ = "convidado"

    id: Optional[int] = Field(default=None, primary_key=True)
    funcionario_associado_id: Optional[int] = Field(default=None, foreign_key="funcionario.id")
    nome: str = Field(max_length=100)
    cpf: str = Field(max_length=11, unique=True)
    email: str = Field(max_length=100, unique=True)
    externo: bool

    funcionario_associado: Optional[Funcionario] = Relationship(back_populates="convidados_associados")
    convites: List["Convite"] = Relationship(back_populates="convidado")


class Convite(SQLModel, table=True):
    __tablename__ = "convite"

    id: Optional[int] = Field(default=None, primary_key=True)
    cota_id: int = Field(foreign_key="cota_cortesia.id")
    convidado_id: int = Field(foreign_key="convidado.id")
    funcionario_convidador_id: int = Field(foreign_key="funcionario.id")

    status: str = Field(max_length=20)

    cota: Optional[CotaCortesia] = Relationship(back_populates="convites")
    convidado: Optional[Convidado] = Relationship(back_populates="convites")
    funcionario_convidador: Optional[Funcionario] = Relationship(back_populates="convites_feitos")


# =========================
# QUESTIONÁRIO (CONFIG + RESPOSTAS)
# =========================


class QuestionarioPagina(SQLModel, table=True):
    __tablename__ = "questionario_pagina"

    id: Optional[int] = Field(default=None, primary_key=True)
    evento_id: int = Field(foreign_key="evento.id")
    ordem: int
    titulo: str = Field(max_length=200)
    descricao: Optional[str] = None

    evento: Optional[Evento] = Relationship(back_populates="paginas_questionario")
    perguntas: List["QuestionarioPergunta"] = Relationship(back_populates="pagina")


class QuestionarioPergunta(SQLModel, table=True):
    __tablename__ = "questionario_pergunta"

    id: Optional[int] = Field(default=None, primary_key=True)
    pagina_id: int = Field(foreign_key="questionario_pagina.id")
    ordem: int
    texto: str = Field(max_length=500)
    tipo: TipoPergunta
    obrigatoria: bool = Field(default=False)

    pagina: Optional[QuestionarioPagina] = Relationship(back_populates="perguntas")
    opcoes: List["QuestionarioOpcao"] = Relationship(back_populates="pergunta")
    respostas: List["QuestionarioRespostaPergunta"] = Relationship(back_populates="pergunta")


class QuestionarioOpcao(SQLModel, table=True):
    __tablename__ = "questionario_opcao"

    id: Optional[int] = Field(default=None, primary_key=True)
    pergunta_id: int = Field(foreign_key="questionario_pergunta.id")
    ordem: int
    texto: str = Field(max_length=200)
    valor_numerico: Optional[int] = None

    pergunta: Optional[QuestionarioPergunta] = Relationship(back_populates="opcoes")
    respostas_opcao: List["QuestionarioRespostaOpcao"] = Relationship(back_populates="opcao")


class QuestionarioResposta(SQLModel, table=True):
    __tablename__ = "questionario_resposta"

    id: Optional[int] = Field(default=None, primary_key=True)
    evento_id: int = Field(foreign_key="evento.id")
    ativacao_id: Optional[int] = Field(default=None, foreign_key="ativacao.id")
    lead_id: Optional[int] = Field(default=None, foreign_key="lead.id")

    data_resposta: datetime = Field(default_factory=now_utc)

    evento: Optional[Evento] = Relationship(back_populates="respostas_questionario")
    ativacao: Optional[Ativacao] = Relationship(back_populates="respostas_questionario")
    lead: Optional[Lead] = Relationship(back_populates="respostas_questionario")

    respostas_pergunta: List["QuestionarioRespostaPergunta"] = Relationship(back_populates="resposta")


class QuestionarioRespostaPergunta(SQLModel, table=True):
    __tablename__ = "questionario_resposta_pergunta"

    id: Optional[int] = Field(default=None, primary_key=True)
    resposta_id: int = Field(foreign_key="questionario_resposta.id")
    pergunta_id: int = Field(foreign_key="questionario_pergunta.id")

    valor_texto: Optional[str] = None
    valor_numerico: Optional[Decimal] = None
    valor_data: Optional[date] = None

    resposta: Optional[QuestionarioResposta] = Relationship(back_populates="respostas_pergunta")
    pergunta: Optional[QuestionarioPergunta] = Relationship(back_populates="respostas")
    opcoes_marcadas: List["QuestionarioRespostaOpcao"] = Relationship(back_populates="resposta_pergunta")


class QuestionarioRespostaOpcao(SQLModel, table=True):
    __tablename__ = "questionario_resposta_opcao"

    id: Optional[int] = Field(default=None, primary_key=True)
    resposta_pergunta_id: int = Field(foreign_key="questionario_resposta_pergunta.id")
    opcao_id: int = Field(foreign_key="questionario_opcao.id")

    resposta_pergunta: Optional[QuestionarioRespostaPergunta] = Relationship(back_populates="opcoes_marcadas")
    opcao: Optional[QuestionarioOpcao] = Relationship(back_populates="respostas_opcao")


# =========================
# FORMULÁRIO DE LEAD / LANDING
# =========================


class FormularioLandingTemplate(SQLModel, table=True):
    __tablename__ = "formulario_landing_template"

    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(max_length=100, unique=True)
    html_conteudo: str
    css_conteudo: Optional[str] = Field(default=None)
    criado_em: datetime = Field(default_factory=now_utc)

    configuracoes: List["FormularioLeadConfig"] = Relationship(back_populates="template")


class FormularioLeadConfig(SQLModel, table=True):
    __tablename__ = "formulario_lead_config"

    id: Optional[int] = Field(default=None, primary_key=True)
    evento_id: int = Field(foreign_key="evento.id")
    nome: str = Field(max_length=100)
    descricao: Optional[str] = Field(default=None, max_length=240)
    template_id: Optional[int] = Field(default=None, foreign_key="formulario_landing_template.id")

    url_landing: Optional[str] = Field(default=None, max_length=500)
    url_promotor: Optional[str] = Field(default=None, max_length=500)
    url_questionario: Optional[str] = Field(default=None, max_length=500)
    url_api: Optional[str] = Field(default=None, max_length=500)

    criado_em: datetime = Field(default_factory=now_utc)
    atualizado_em: datetime = Field(default_factory=now_utc)

    evento: Optional[Evento] = Relationship()
    template: Optional[FormularioLandingTemplate] = Relationship(back_populates="configuracoes")
    campos: List["FormularioLeadCampo"] = Relationship(back_populates="config")


class FormularioLeadCampo(SQLModel, table=True):
    __tablename__ = "formulario_lead_campo"

    id: Optional[int] = Field(default=None, primary_key=True)
    config_id: int = Field(foreign_key="formulario_lead_config.id")
    nome_campo: str = Field(max_length=80)
    obrigatorio: bool = Field(default=True)
    ordem: int

    config: Optional[FormularioLeadConfig] = Relationship(back_populates="campos")
