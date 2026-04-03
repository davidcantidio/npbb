"""Modelos auxiliares de eventos: convites, questionario e configuracao de landing."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from app.db.metadata import SQLModel
from app.models.models import (
    SolicitacaoIngressoStatus,
    SolicitacaoIngressoTipo,
    TipoPergunta,
    now_utc,
)

if TYPE_CHECKING:
    from app.models.models import Ativacao, Diretoria, Evento, Funcionario, Lead, Usuario


class CotaCortesia(SQLModel, table=True):
    __tablename__ = "cota_cortesia"
    __table_args__ = (UniqueConstraint("evento_id", "diretoria_id"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    evento_id: int = Field(foreign_key="evento.id")
    diretoria_id: int = Field(foreign_key="diretoria.id", index=True)
    quantidade: int

    evento: Optional["Evento"] = Relationship(back_populates="cotas")
    diretoria: Optional["Diretoria"] = Relationship(back_populates="cotas")
    convites: List["Convite"] = Relationship(back_populates="cota")
    solicitacoes: List["SolicitacaoIngresso"] = Relationship(back_populates="cota")


class SolicitacaoIngresso(SQLModel, table=True):
    __tablename__ = "solicitacao_ingresso"

    id: Optional[int] = Field(default=None, primary_key=True)
    cota_id: int = Field(foreign_key="cota_cortesia.id", index=True)
    evento_id: int = Field(foreign_key="evento.id")
    diretoria_id: int = Field(foreign_key="diretoria.id")
    solicitante_usuario_id: int = Field(foreign_key="usuario.id")
    solicitante_email: str = Field(max_length=120)
    tipo: SolicitacaoIngressoTipo
    indicado_email: Optional[str] = Field(default=None, max_length=120)
    status: SolicitacaoIngressoStatus
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(default_factory=now_utc)

    cota: Optional["CotaCortesia"] = Relationship(back_populates="solicitacoes")
    evento: Optional["Evento"] = Relationship()
    diretoria: Optional["Diretoria"] = Relationship()
    solicitante_usuario: Optional["Usuario"] = Relationship()


class Convidado(SQLModel, table=True):
    __tablename__ = "convidado"

    id: Optional[int] = Field(default=None, primary_key=True)
    funcionario_associado_id: Optional[int] = Field(default=None, foreign_key="funcionario.id")
    nome: str = Field(max_length=100)
    cpf: str = Field(max_length=11, unique=True)
    email: str = Field(max_length=100, unique=True)
    externo: bool

    funcionario_associado: Optional["Funcionario"] = Relationship(
        back_populates="convidados_associados"
    )
    convites: List["Convite"] = Relationship(back_populates="convidado")


class Convite(SQLModel, table=True):
    __tablename__ = "convite"

    id: Optional[int] = Field(default=None, primary_key=True)
    cota_id: int = Field(foreign_key="cota_cortesia.id")
    convidado_id: int = Field(foreign_key="convidado.id")
    funcionario_convidador_id: int = Field(foreign_key="funcionario.id")
    status: str = Field(max_length=20)

    cota: Optional["CotaCortesia"] = Relationship(back_populates="convites")
    convidado: Optional["Convidado"] = Relationship(back_populates="convites")
    funcionario_convidador: Optional["Funcionario"] = Relationship(back_populates="convites_feitos")


class QuestionarioPagina(SQLModel, table=True):
    __tablename__ = "questionario_pagina"

    id: Optional[int] = Field(default=None, primary_key=True)
    evento_id: int = Field(foreign_key="evento.id")
    ordem: int
    titulo: str = Field(max_length=200)
    descricao: Optional[str] = None

    evento: Optional["Evento"] = Relationship(back_populates="paginas_questionario")
    perguntas: List["QuestionarioPergunta"] = Relationship(back_populates="pagina")


class QuestionarioPergunta(SQLModel, table=True):
    __tablename__ = "questionario_pergunta"

    id: Optional[int] = Field(default=None, primary_key=True)
    pagina_id: int = Field(foreign_key="questionario_pagina.id")
    ordem: int
    texto: str = Field(max_length=500)
    tipo: TipoPergunta
    obrigatoria: bool = Field(default=False)

    pagina: Optional["QuestionarioPagina"] = Relationship(back_populates="perguntas")
    opcoes: List["QuestionarioOpcao"] = Relationship(back_populates="pergunta")
    respostas: List["QuestionarioRespostaPergunta"] = Relationship(back_populates="pergunta")


class QuestionarioOpcao(SQLModel, table=True):
    __tablename__ = "questionario_opcao"

    id: Optional[int] = Field(default=None, primary_key=True)
    pergunta_id: int = Field(foreign_key="questionario_pergunta.id")
    ordem: int
    texto: str = Field(max_length=200)
    valor_numerico: Optional[int] = None

    pergunta: Optional["QuestionarioPergunta"] = Relationship(back_populates="opcoes")
    respostas_opcao: List["QuestionarioRespostaOpcao"] = Relationship(back_populates="opcao")


class QuestionarioResposta(SQLModel, table=True):
    __tablename__ = "questionario_resposta"

    id: Optional[int] = Field(default=None, primary_key=True)
    evento_id: int = Field(foreign_key="evento.id")
    ativacao_id: Optional[int] = Field(default=None, foreign_key="ativacao.id")
    lead_id: Optional[int] = Field(default=None, foreign_key="lead.id")
    data_resposta: datetime = Field(default_factory=now_utc)

    evento: Optional["Evento"] = Relationship(back_populates="respostas_questionario")
    ativacao: Optional["Ativacao"] = Relationship(back_populates="respostas_questionario")
    lead: Optional["Lead"] = Relationship(back_populates="respostas_questionario")
    respostas_pergunta: List["QuestionarioRespostaPergunta"] = Relationship(
        back_populates="resposta"
    )


class QuestionarioRespostaPergunta(SQLModel, table=True):
    __tablename__ = "questionario_resposta_pergunta"

    id: Optional[int] = Field(default=None, primary_key=True)
    resposta_id: int = Field(foreign_key="questionario_resposta.id")
    pergunta_id: int = Field(foreign_key="questionario_pergunta.id")
    valor_texto: Optional[str] = None
    valor_numerico: Optional[Decimal] = None
    valor_data: Optional[date] = None

    resposta: Optional["QuestionarioResposta"] = Relationship(back_populates="respostas_pergunta")
    pergunta: Optional["QuestionarioPergunta"] = Relationship(back_populates="respostas")
    opcoes_marcadas: List["QuestionarioRespostaOpcao"] = Relationship(
        back_populates="resposta_pergunta"
    )


class QuestionarioRespostaOpcao(SQLModel, table=True):
    __tablename__ = "questionario_resposta_opcao"

    id: Optional[int] = Field(default=None, primary_key=True)
    resposta_pergunta_id: int = Field(foreign_key="questionario_resposta_pergunta.id")
    opcao_id: int = Field(foreign_key="questionario_opcao.id")

    resposta_pergunta: Optional["QuestionarioRespostaPergunta"] = Relationship(
        back_populates="opcoes_marcadas"
    )
    opcao: Optional["QuestionarioOpcao"] = Relationship(back_populates="respostas_opcao")


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
    url_checkin_sem_qr: Optional[str] = Field(default=None, max_length=500)
    url_questionario: Optional[str] = Field(default=None, max_length=500)
    url_api: Optional[str] = Field(default=None, max_length=500)
    criado_em: datetime = Field(default_factory=now_utc)
    atualizado_em: datetime = Field(default_factory=now_utc)

    evento: Optional["Evento"] = Relationship()
    template: Optional["FormularioLandingTemplate"] = Relationship(back_populates="configuracoes")
    campos: List["FormularioLeadCampo"] = Relationship(back_populates="config")


class FormularioLeadCampo(SQLModel, table=True):
    __tablename__ = "formulario_lead_campo"

    id: Optional[int] = Field(default=None, primary_key=True)
    config_id: int = Field(foreign_key="formulario_lead_config.id")
    nome_campo: str = Field(max_length=80)
    obrigatorio: bool = Field(default=True)
    ordem: int

    config: Optional["FormularioLeadConfig"] = Relationship(back_populates="campos")
