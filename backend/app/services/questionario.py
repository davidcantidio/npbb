"""Helpers do modulo de questionario (estrutura por evento)."""

from __future__ import annotations

from collections import defaultdict

from sqlalchemy import delete as sa_delete
from sqlmodel import Session, select

from app.models.models import QuestionarioOpcao, QuestionarioPagina, QuestionarioPergunta
from app.schemas.questionario import QuestionarioEstruturaWrite


def load_questionario_estrutura(session: Session, *, evento_id: int) -> list[QuestionarioPagina]:
    """Carrega paginas/perguntas/opcoes ordenadas por ordem (fallback por id)."""
    paginas = session.exec(
        select(QuestionarioPagina)
        .where(QuestionarioPagina.evento_id == evento_id)
        .order_by(QuestionarioPagina.ordem, QuestionarioPagina.id)
    ).all()
    if not paginas:
        return []

    pagina_ids = [pagina.id for pagina in paginas if pagina.id is not None]
    perguntas = session.exec(
        select(QuestionarioPergunta)
        .where(QuestionarioPergunta.pagina_id.in_(pagina_ids))
        .order_by(
            QuestionarioPergunta.pagina_id,
            QuestionarioPergunta.ordem,
            QuestionarioPergunta.id,
        )
    ).all()

    pergunta_ids = [pergunta.id for pergunta in perguntas if pergunta.id is not None]
    opcoes = []
    if pergunta_ids:
        opcoes = session.exec(
            select(QuestionarioOpcao)
            .where(QuestionarioOpcao.pergunta_id.in_(pergunta_ids))
            .order_by(
                QuestionarioOpcao.pergunta_id,
                QuestionarioOpcao.ordem,
                QuestionarioOpcao.id,
            )
        ).all()

    opcoes_por_pergunta: dict[int, list[QuestionarioOpcao]] = defaultdict(list)
    for opcao in opcoes:
        opcoes_por_pergunta[opcao.pergunta_id].append(opcao)

    for pergunta in perguntas:
        if pergunta.id is None:
            pergunta.opcoes = []
        else:
            pergunta.opcoes = opcoes_por_pergunta.get(pergunta.id, [])

    perguntas_por_pagina: dict[int, list[QuestionarioPergunta]] = defaultdict(list)
    for pergunta in perguntas:
        perguntas_por_pagina[pergunta.pagina_id].append(pergunta)

    for pagina in paginas:
        if pagina.id is None:
            pagina.perguntas = []
        else:
            pagina.perguntas = perguntas_por_pagina.get(pagina.id, [])

    return paginas


def replace_questionario_estrutura(
    session: Session,
    *,
    evento_id: int,
    payload: QuestionarioEstruturaWrite,
) -> list[QuestionarioPagina]:
    """Substitui toda a estrutura do questionario (replace-all)."""
    pagina_ids = session.exec(
        select(QuestionarioPagina.id).where(QuestionarioPagina.evento_id == evento_id)
    ).all()
    pagina_ids = [pid for pid in pagina_ids if pid is not None]
    if pagina_ids:
        pergunta_ids = session.exec(
            select(QuestionarioPergunta.id).where(QuestionarioPergunta.pagina_id.in_(pagina_ids))
        ).all()
        pergunta_ids = [pid for pid in pergunta_ids if pid is not None]
        if pergunta_ids:
            session.exec(sa_delete(QuestionarioOpcao).where(QuestionarioOpcao.pergunta_id.in_(pergunta_ids)))
            session.exec(sa_delete(QuestionarioPergunta).where(QuestionarioPergunta.id.in_(pergunta_ids)))
        session.exec(sa_delete(QuestionarioPagina).where(QuestionarioPagina.id.in_(pagina_ids)))

    try:
        for pagina in payload.paginas:
            pagina_model = QuestionarioPagina(
                evento_id=evento_id,
                ordem=pagina.ordem,
                titulo=pagina.titulo,
                descricao=pagina.descricao,
            )
            session.add(pagina_model)
            session.flush()

            for pergunta in pagina.perguntas:
                pergunta_model = QuestionarioPergunta(
                    pagina_id=pagina_model.id,
                    ordem=pergunta.ordem,
                    tipo=pergunta.tipo,
                    texto=pergunta.texto,
                    obrigatoria=pergunta.obrigatoria,
                )
                session.add(pergunta_model)
                session.flush()

                for opcao in pergunta.opcoes:
                    session.add(
                        QuestionarioOpcao(
                            pergunta_id=pergunta_model.id,
                            ordem=opcao.ordem,
                            texto=opcao.texto,
                        )
                    )

        session.commit()
    except Exception:
        session.rollback()
        raise

    return load_questionario_estrutura(session, evento_id=evento_id)
