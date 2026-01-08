"""Helpers do modulo de questionario (estrutura por evento)."""

from __future__ import annotations

from collections import defaultdict

from sqlmodel import Session, select

from app.models.models import QuestionarioOpcao, QuestionarioPagina, QuestionarioPergunta


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
