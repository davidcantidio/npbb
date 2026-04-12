"""Servico de inventario e reconciliacao de ingressos v2 (snapshot materializado)."""

from __future__ import annotations

from uuid import uuid4

from sqlalchemy import func
from sqlmodel import Session, select

from app.models.ingressos_v2_models import (
    AuditoriaDesbloqueioInventario,
    ConfiguracaoIngressoEvento,
    ConfiguracaoIngressoEventoTipo,
    DesbloqueioManualInventario,
    DistribuicaoIngresso,
    InventarioIngresso,
    PrevisaoIngresso,
    RecebimentoIngresso,
)
from app.models.models import (
    ModoFornecimento,
    StatusDestinatario,
    TipoBloqueioInventario,
    TipoIngresso,
)

MSG_CONFIG_NOT_FOUND = "Configuracao de ingressos nao encontrada para o evento"
MSG_TIPO_INATIVO = "Tipo de ingresso nao esta ativo para o evento"
MSG_RECEBIMENTO_QUANTIDADE_INVALIDA = "Quantidade do recebimento deve ser positiva"
MSG_RECEBIMENTO_MODO_INVALIDO = (
    "Recebimentos so podem ser registados quando o evento esta em modo externo_recebido"
)
MSG_DESBLOQUEIO_QUANTIDADE_INVALIDA = "Quantidade do desbloqueio manual deve ser positiva"
MSG_DESBLOQUEIO_MODO_INVALIDO = (
    "Desbloqueio manual so pode ser registado quando o evento esta em modo externo_recebido"
)
MSG_DESBLOQUEIO_SEM_BLOQUEIO = "Nao ha bloqueio ativo para desbloqueio manual"
MSG_DESBLOQUEIO_EXCEDE_BLOQUEIO = "Quantidade solicitada excede o bloqueado atual"
MSG_DESBLOQUEIO_USUARIO_OBRIGATORIO = "Usuario do desbloqueio manual e obrigatorio"
MSG_DESBLOQUEIO_MOTIVO_OBRIGATORIO = "Motivo do desbloqueio manual e obrigatorio"


def _bloqueado_por_falta_de_recebimento(planejado: int, recebido_confirmado: int) -> int:
    """Quantidade planejada ainda nao coberta por recebimentos."""
    return max(planejado - recebido_confirmado, 0)


def _bloqueado_por_excesso_recebido(planejado: int, recebido_confirmado: int) -> int:
    """Ingressos recebidos alem do planejado, bloqueados ate aumento de previsao."""
    return max(recebido_confirmado - planejado, 0)


def _tipo_e_quantidade_bloqueio_base(
    planejado: int, recebido_confirmado: int
) -> tuple[TipoBloqueioInventario | None, int]:
    bloqueado_por_recebimento = _bloqueado_por_falta_de_recebimento(planejado, recebido_confirmado)
    if bloqueado_por_recebimento > 0:
        return TipoBloqueioInventario.FALTA_RECEBIMENTO, bloqueado_por_recebimento

    bloqueado_por_excesso = _bloqueado_por_excesso_recebido(planejado, recebido_confirmado)
    if bloqueado_por_excesso > 0:
        return TipoBloqueioInventario.EXCESSO_RECEBIDO, bloqueado_por_excesso

    return None, 0


def _capacidade_distribuivel_base(planejado: int, recebido_confirmado: int) -> int:
    return min(recebido_confirmado, planejado)


def _get_configuracao(session: Session, evento_id: int) -> ConfiguracaoIngressoEvento:
    configuracao = session.exec(
        select(ConfiguracaoIngressoEvento).where(ConfiguracaoIngressoEvento.evento_id == evento_id)
    ).first()
    if configuracao is None:
        raise ValueError(MSG_CONFIG_NOT_FOUND)
    return configuracao


def _tipo_ingresso_ativo_no_evento(
    session: Session, *, configuracao_id: int, tipo_ingresso: TipoIngresso
) -> bool:
    row = session.exec(
        select(ConfiguracaoIngressoEventoTipo.id).where(
            ConfiguracaoIngressoEventoTipo.configuracao_id == configuracao_id,
            ConfiguracaoIngressoEventoTipo.tipo_ingresso == tipo_ingresso,
        )
    ).first()
    return row is not None


def _planejado_previsao(
    session: Session, *, evento_id: int, diretoria_id: int, tipo_ingresso: TipoIngresso
) -> int:
    previsao = session.exec(
        select(PrevisaoIngresso).where(
            PrevisaoIngresso.evento_id == evento_id,
            PrevisaoIngresso.diretoria_id == diretoria_id,
            PrevisaoIngresso.tipo_ingresso == tipo_ingresso,
        )
    ).first()
    return int(previsao.quantidade) if previsao is not None else 0


def _total_recebido_confirmado(
    session: Session, *, evento_id: int, diretoria_id: int, tipo_ingresso: TipoIngresso
) -> int:
    total = session.exec(
        select(func.coalesce(func.sum(RecebimentoIngresso.quantidade), 0)).where(
            RecebimentoIngresso.evento_id == evento_id,
            RecebimentoIngresso.diretoria_id == diretoria_id,
            RecebimentoIngresso.tipo_ingresso == tipo_ingresso,
        )
    ).one()
    return int(total or 0)


def _total_distribuido_ativo(
    session: Session, *, evento_id: int, diretoria_id: int, tipo_ingresso: TipoIngresso
) -> int:
    total = session.exec(
        select(func.count()).select_from(DistribuicaoIngresso).where(
            DistribuicaoIngresso.evento_id == evento_id,
            DistribuicaoIngresso.diretoria_id == diretoria_id,
            DistribuicaoIngresso.tipo_ingresso == tipo_ingresso,
            DistribuicaoIngresso.status_destinatario != StatusDestinatario.CANCELADO,
        )
    ).one()
    return int(total or 0)


def _get_desbloqueio_manual(
    session: Session, *, evento_id: int, diretoria_id: int, tipo_ingresso: TipoIngresso
) -> DesbloqueioManualInventario | None:
    return session.exec(
        select(DesbloqueioManualInventario).where(
            DesbloqueioManualInventario.evento_id == evento_id,
            DesbloqueioManualInventario.diretoria_id == diretoria_id,
            DesbloqueioManualInventario.tipo_ingresso == tipo_ingresso,
        )
    ).first()


def _clear_desbloqueio_manual(
    session: Session, desbloqueio: DesbloqueioManualInventario | None
) -> None:
    if desbloqueio is None:
        return
    session.delete(desbloqueio)
    session.flush()


def _quantidade_desbloqueio_manual_efetiva(
    session: Session,
    *,
    evento_id: int,
    diretoria_id: int,
    tipo_ingresso: TipoIngresso,
    tipo_bloqueio_base: TipoBloqueioInventario | None,
    bloqueio_base: int,
) -> int:
    desbloqueio = _get_desbloqueio_manual(
        session,
        evento_id=evento_id,
        diretoria_id=diretoria_id,
        tipo_ingresso=tipo_ingresso,
    )
    if desbloqueio is None:
        return 0

    if (
        tipo_bloqueio_base is None
        or bloqueio_base <= 0
        or desbloqueio.tipo_bloqueio_atual != tipo_bloqueio_base
    ):
        _clear_desbloqueio_manual(session, desbloqueio)
        return 0

    quantidade_efetiva = min(int(desbloqueio.quantidade_restante), bloqueio_base)
    if quantidade_efetiva <= 0:
        _clear_desbloqueio_manual(session, desbloqueio)
        return 0

    if int(desbloqueio.quantidade_restante) != quantidade_efetiva:
        desbloqueio.quantidade_restante = quantidade_efetiva
        session.add(desbloqueio)

    return quantidade_efetiva


def calcular_inventario(
    session: Session,
    *,
    evento_id: int,
    diretoria_id: int,
    tipo_ingresso: TipoIngresso,
) -> InventarioIngresso:
    """Recalcula e persiste o snapshot de inventario para (evento, diretoria, tipo).

    O snapshot continua a agregar `PrevisaoIngresso`, `RecebimentoIngresso` e
    `DistribuicaoIngresso`. O desbloqueio manual e modelado como override persistido
    e temporal sobre o bloqueio base calculado a partir de planejamento e
    recebimentos. Se o contexto do bloqueio deixar de existir, o override e limpo
    para nao reativar credito antigo em estados futuros.
    """
    configuracao = _get_configuracao(session, evento_id)
    if not _tipo_ingresso_ativo_no_evento(
        session, configuracao_id=int(configuracao.id), tipo_ingresso=tipo_ingresso
    ):
        raise ValueError(MSG_TIPO_INATIVO)

    planejado = _planejado_previsao(
        session, evento_id=evento_id, diretoria_id=diretoria_id, tipo_ingresso=tipo_ingresso
    )
    distribuido = _total_distribuido_ativo(
        session, evento_id=evento_id, diretoria_id=diretoria_id, tipo_ingresso=tipo_ingresso
    )

    if configuracao.modo_fornecimento == ModoFornecimento.INTERNO_EMITIDO_COM_QR:
        _clear_desbloqueio_manual(
            session,
            _get_desbloqueio_manual(
                session,
                evento_id=evento_id,
                diretoria_id=diretoria_id,
                tipo_ingresso=tipo_ingresso,
            ),
        )
        recebido_confirmado = 0
        bloqueado = 0
        disponivel = max(planejado - distribuido, 0)
    else:
        recebido_confirmado = _total_recebido_confirmado(
            session, evento_id=evento_id, diretoria_id=diretoria_id, tipo_ingresso=tipo_ingresso
        )
        tipo_bloqueio_base, bloqueio_base = _tipo_e_quantidade_bloqueio_base(
            planejado, recebido_confirmado
        )
        quantidade_desbloqueio_manual = _quantidade_desbloqueio_manual_efetiva(
            session,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=tipo_ingresso,
            tipo_bloqueio_base=tipo_bloqueio_base,
            bloqueio_base=bloqueio_base,
        )
        bloqueado = max(bloqueio_base - quantidade_desbloqueio_manual, 0)
        capacidade_distribuivel = (
            _capacidade_distribuivel_base(planejado, recebido_confirmado)
            + quantidade_desbloqueio_manual
        )
        disponivel = max(capacidade_distribuivel - distribuido, 0)

    inv = session.exec(
        select(InventarioIngresso).where(
            InventarioIngresso.evento_id == evento_id,
            InventarioIngresso.diretoria_id == diretoria_id,
            InventarioIngresso.tipo_ingresso == tipo_ingresso,
        )
    ).first()

    if inv is None:
        inv = InventarioIngresso(
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=tipo_ingresso,
            planejado=planejado,
            recebido_confirmado=recebido_confirmado,
            bloqueado=bloqueado,
            disponivel=disponivel,
            distribuido=distribuido,
        )
        session.add(inv)
    else:
        inv.planejado = planejado
        inv.recebido_confirmado = recebido_confirmado
        inv.bloqueado = bloqueado
        inv.disponivel = disponivel
        inv.distribuido = distribuido
        session.add(inv)

    session.flush()
    session.refresh(inv)
    return inv


def registrar_recebimento(
    session: Session,
    *,
    evento_id: int,
    diretoria_id: int,
    tipo_ingresso: TipoIngresso,
    quantidade: int,
    artifact_file_path: str | None = None,
    artifact_link: str | None = None,
    artifact_instructions: str | None = None,
    correlation_id: str | None = None,
) -> tuple[RecebimentoIngresso, InventarioIngresso]:
    """Regista um recebimento externo, persiste a linha e atualiza o snapshot."""
    if quantidade <= 0:
        raise ValueError(MSG_RECEBIMENTO_QUANTIDADE_INVALIDA)

    configuracao = _get_configuracao(session, evento_id)
    if configuracao.modo_fornecimento != ModoFornecimento.EXTERNO_RECEBIDO:
        raise ValueError(MSG_RECEBIMENTO_MODO_INVALIDO)

    if not _tipo_ingresso_ativo_no_evento(
        session, configuracao_id=int(configuracao.id), tipo_ingresso=tipo_ingresso
    ):
        raise ValueError(MSG_TIPO_INATIVO)

    corr = correlation_id if correlation_id is not None else str(uuid4())
    recebimento = RecebimentoIngresso(
        evento_id=evento_id,
        diretoria_id=diretoria_id,
        tipo_ingresso=tipo_ingresso,
        quantidade=quantidade,
        artifact_file_path=artifact_file_path,
        artifact_link=artifact_link,
        artifact_instructions=artifact_instructions,
        correlation_id=corr,
    )
    session.add(recebimento)
    session.flush()

    inventario = calcular_inventario(
        session,
        evento_id=evento_id,
        diretoria_id=diretoria_id,
        tipo_ingresso=tipo_ingresso,
    )
    return recebimento, inventario


def desbloqueio_manual(
    session: Session,
    *,
    evento_id: int,
    diretoria_id: int,
    tipo_ingresso: TipoIngresso,
    quantidade: int | None,
    usuario_id: int | None,
    motivo: str,
    correlation_id: str | None = None,
) -> tuple[AuditoriaDesbloqueioInventario, InventarioIngresso]:
    """Aplica override de admin sobre o bloqueio atual sem alterar recebimentos ou previsao."""
    if quantidade is not None and quantidade <= 0:
        raise ValueError(MSG_DESBLOQUEIO_QUANTIDADE_INVALIDA)
    if usuario_id is None:
        raise ValueError(MSG_DESBLOQUEIO_USUARIO_OBRIGATORIO)
    if not motivo or not motivo.strip():
        raise ValueError(MSG_DESBLOQUEIO_MOTIVO_OBRIGATORIO)

    configuracao = _get_configuracao(session, evento_id)
    if configuracao.modo_fornecimento != ModoFornecimento.EXTERNO_RECEBIDO:
        raise ValueError(MSG_DESBLOQUEIO_MODO_INVALIDO)

    if not _tipo_ingresso_ativo_no_evento(
        session, configuracao_id=int(configuracao.id), tipo_ingresso=tipo_ingresso
    ):
        raise ValueError(MSG_TIPO_INATIVO)

    inventario_antes = calcular_inventario(
        session,
        evento_id=evento_id,
        diretoria_id=diretoria_id,
        tipo_ingresso=tipo_ingresso,
    )
    bloqueado_antes = int(inventario_antes.bloqueado)
    tipo_bloqueio_base, bloqueio_base = _tipo_e_quantidade_bloqueio_base(
        int(inventario_antes.planejado), int(inventario_antes.recebido_confirmado)
    )
    if tipo_bloqueio_base is None or bloqueio_base <= 0 or bloqueado_antes <= 0:
        raise ValueError(MSG_DESBLOQUEIO_SEM_BLOQUEIO)

    quantidade_desbloqueio = bloqueado_antes if quantidade is None else quantidade
    if quantidade_desbloqueio > bloqueado_antes:
        raise ValueError(MSG_DESBLOQUEIO_EXCEDE_BLOQUEIO)

    desbloqueio = _get_desbloqueio_manual(
        session,
        evento_id=evento_id,
        diretoria_id=diretoria_id,
        tipo_ingresso=tipo_ingresso,
    )
    quantidade_existente = 0
    if desbloqueio is not None:
        quantidade_existente = int(desbloqueio.quantidade_restante)

    nova_quantidade = quantidade_existente + quantidade_desbloqueio
    if desbloqueio is None:
        desbloqueio = DesbloqueioManualInventario(
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=tipo_ingresso,
            tipo_bloqueio_atual=tipo_bloqueio_base,
            quantidade_restante=nova_quantidade,
        )
    else:
        desbloqueio.tipo_bloqueio_atual = tipo_bloqueio_base
        desbloqueio.quantidade_restante = nova_quantidade
    session.add(desbloqueio)
    session.flush()

    inventario_depois = calcular_inventario(
        session,
        evento_id=evento_id,
        diretoria_id=diretoria_id,
        tipo_ingresso=tipo_ingresso,
    )

    auditoria = AuditoriaDesbloqueioInventario(
        evento_id=evento_id,
        diretoria_id=diretoria_id,
        tipo_ingresso=tipo_ingresso,
        usuario_id=usuario_id,
        bloqueado_antes=bloqueado_antes,
        bloqueado_depois=int(inventario_depois.bloqueado),
        quantidade=quantidade_desbloqueio,
        motivo=motivo.strip(),
        correlation_id=correlation_id or str(uuid4()),
    )
    session.add(auditoria)
    session.flush()
    session.refresh(inventario_depois)
    session.refresh(auditoria)
    return auditoria, inventario_depois
