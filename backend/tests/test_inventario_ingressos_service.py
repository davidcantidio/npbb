"""Testes do servico de inventario / recebimentos (ingressos v2)."""

from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.models.ingressos_v2_models import (
    AuditoriaDesbloqueioInventario,
    DesbloqueioManualInventario,
    ConfiguracaoIngressoEvento,
    ConfiguracaoIngressoEventoTipo,
    DistribuicaoIngresso,
    InventarioIngresso,
    PrevisaoIngresso,
    RecebimentoIngresso,
)
from app.models.models import (
    Agencia,
    Diretoria,
    Evento,
    ModoFornecimento,
    StatusDestinatario,
    StatusEvento,
    TipoIngresso,
    Usuario,
    UsuarioTipo,
)
from app.services.inventario_ingressos import (
    MSG_DESBLOQUEIO_EXCEDE_BLOQUEIO,
    MSG_DESBLOQUEIO_MODO_INVALIDO,
    MSG_DESBLOQUEIO_QUANTIDADE_INVALIDA,
    MSG_DESBLOQUEIO_SEM_BLOQUEIO,
    calcular_inventario,
    desbloqueio_manual,
    registrar_recebimento,
)


def make_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture
def engine():
    eng = make_engine()
    SQLModel.metadata.create_all(eng)
    with Session(eng) as session:
        exists = session.exec(select(StatusEvento).where(StatusEvento.nome == "Previsto")).first()
        if not exists:
            session.add(StatusEvento(nome="Previsto"))
            session.commit()
    return eng


def _seed_evento_com_config_externa(
    session: Session,
    *,
    modo_fornecimento: ModoFornecimento = ModoFornecimento.EXTERNO_RECEBIDO,
    tipos_ativos: tuple[TipoIngresso, ...] = (TipoIngresso.PISTA,),
    previsao_quantidade: int | None = 100,
) -> tuple[int, int]:
    agencia = Agencia(nome="InvTest", dominio="inv.test", lote=1)
    session.add(agencia)
    session.commit()
    session.refresh(agencia)

    diretoria = Diretoria(nome="Dir Inv")
    session.add(diretoria)
    session.commit()
    session.refresh(diretoria)

    status = session.exec(select(StatusEvento).where(StatusEvento.nome == "Previsto")).first()
    assert status and status.id
    evento = Evento(
        nome="Evento Inv",
        concorrencia=False,
        cidade="Brasilia",
        estado="DF",
        agencia_id=int(agencia.id),
        diretoria_id=int(diretoria.id),
        status_id=int(status.id),
        data_inicio_prevista=date(2026, 5, 1),
        data_fim_prevista=date(2026, 5, 2),
    )
    session.add(evento)
    session.commit()
    session.refresh(evento)

    config = ConfiguracaoIngressoEvento(
        evento_id=int(evento.id),
        modo_fornecimento=modo_fornecimento,
    )
    session.add(config)
    session.commit()
    session.refresh(config)
    for tipo_ingresso in tipos_ativos:
        session.add(
            ConfiguracaoIngressoEventoTipo(
                configuracao_id=int(config.id),
                tipo_ingresso=tipo_ingresso,
            )
        )
    session.commit()

    if previsao_quantidade is not None:
        previsao = PrevisaoIngresso(
            evento_id=int(evento.id),
            diretoria_id=int(diretoria.id),
            tipo_ingresso=TipoIngresso.PISTA,
            quantidade=previsao_quantidade,
        )
        session.add(previsao)
        session.commit()

    return int(evento.id), int(diretoria.id)


def _seed_npbb_user(session: Session, *, email: str = "npbb-inv@example.com") -> Usuario:
    user = Usuario(
        email=email,
        password_hash="hash-test",
        tipo_usuario=UsuarioTipo.NPBB,
        ativo=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def test_registrar_recebimento_parcial_bloqueia_falta(engine):
    with Session(engine) as s:
        evento_id, diretoria_id = _seed_evento_com_config_externa(s)

        rec, inv = registrar_recebimento(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
            quantidade=50,
            artifact_link="https://drive.example/x",
        )
        s.commit()

        assert rec.quantidade == 50
        assert inv.planejado == 100
        assert inv.recebido_confirmado == 50
        assert inv.bloqueado == 50
        assert inv.disponivel == 50
        assert inv.distribuido == 0


def test_registrar_segundo_recebimento_desbloqueia(engine):
    with Session(engine) as s:
        evento_id, diretoria_id = _seed_evento_com_config_externa(s)

        registrar_recebimento(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
            quantidade=50,
        )
        s.commit()

        _, inv = registrar_recebimento(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
            quantidade=50,
        )
        s.commit()

        assert inv.recebido_confirmado == 100
        assert inv.bloqueado == 0
        assert inv.disponivel == 100


def test_desbloqueio_automatico_recebimentos_incrementais(engine):
    """Quando o total recebido alcanca planejado, o bloqueio por falta zera (plan.md Task 3)."""
    with Session(engine) as s:
        evento_id, diretoria_id = _seed_evento_com_config_externa(s)

        _, inv1 = registrar_recebimento(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
            quantidade=40,
        )
        s.commit()
        assert inv1.recebido_confirmado == 40
        assert inv1.bloqueado == 60
        assert inv1.disponivel == 40

        _, inv2 = registrar_recebimento(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
            quantidade=35,
        )
        s.commit()
        assert inv2.recebido_confirmado == 75
        assert inv2.bloqueado == 25
        assert inv2.disponivel == 75

        _, inv3 = registrar_recebimento(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
            quantidade=25,
        )
        s.commit()
        assert inv3.recebido_confirmado == 100
        assert inv3.bloqueado == 0
        assert inv3.disponivel == 100


def test_registrar_recebimento_com_surplus(engine):
    with Session(engine) as s:
        evento_id, diretoria_id = _seed_evento_com_config_externa(s)

        _, inv = registrar_recebimento(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
            quantidade=120,
        )
        s.commit()

        assert inv.recebido_confirmado == 120
        assert inv.planejado == 100
        assert inv.bloqueado == 20
        assert inv.disponivel == 100


def test_calcular_inventario_liberta_surplus_quando_previsao_aumenta(engine):
    with Session(engine) as s:
        evento_id, diretoria_id = _seed_evento_com_config_externa(s)

        _, inv_inicial = registrar_recebimento(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
            quantidade=120,
        )
        s.commit()

        assert inv_inicial.recebido_confirmado == 120
        assert inv_inicial.planejado == 100
        assert inv_inicial.bloqueado == 20
        assert inv_inicial.disponivel == 100

        previsao = s.exec(
            select(PrevisaoIngresso).where(
                PrevisaoIngresso.evento_id == evento_id,
                PrevisaoIngresso.diretoria_id == diretoria_id,
                PrevisaoIngresso.tipo_ingresso == TipoIngresso.PISTA,
            )
        ).first()
        assert previsao is not None

        previsao.quantidade = 120
        s.add(previsao)
        s.flush()

        inv_recalculado = calcular_inventario(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
        )
        s.commit()

        assert inv_recalculado.id == inv_inicial.id
        assert inv_recalculado.planejado == 120
        assert inv_recalculado.recebido_confirmado == 120
        assert inv_recalculado.bloqueado == 0
        assert inv_recalculado.disponivel == 120


def test_desbloqueio_manual_falta_persiste_auditoria_e_snapshot(engine):
    with Session(engine) as s:
        evento_id, diretoria_id = _seed_evento_com_config_externa(s)
        user = _seed_npbb_user(s, email="npbb-desbloqueio-falta@example.com")

        registrar_recebimento(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
            quantidade=50,
        )
        s.commit()

        auditoria, inv = desbloqueio_manual(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
            quantidade=20,
            usuario_id=int(user.id),
            motivo="Liberacao operacional controlada",
            correlation_id="11111111-2222-3333-4444-555555555555",
        )
        s.commit()

        assert auditoria.quantidade == 20
        assert auditoria.bloqueado_antes == 50
        assert auditoria.bloqueado_depois == 30
        assert auditoria.correlation_id == "11111111-2222-3333-4444-555555555555"
        assert inv.bloqueado == 30
        assert inv.disponivel == 70

        override = s.exec(
            select(DesbloqueioManualInventario).where(
                DesbloqueioManualInventario.evento_id == evento_id,
                DesbloqueioManualInventario.diretoria_id == diretoria_id,
                DesbloqueioManualInventario.tipo_ingresso == TipoIngresso.PISTA,
            )
        ).first()
        assert override is not None
        assert override.tipo_bloqueio_atual.value == "falta_recebimento"
        assert override.quantidade_restante == 20

        audit_rows = s.exec(
            select(AuditoriaDesbloqueioInventario).where(
                AuditoriaDesbloqueioInventario.evento_id == evento_id
            )
        ).all()
        assert len(audit_rows) == 1

        recalculado = calcular_inventario(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
        )
        s.commit()
        assert recalculado.bloqueado == 30
        assert recalculado.disponivel == 70


def test_desbloqueio_manual_excesso_persiste_auditoria_e_snapshot(engine):
    with Session(engine) as s:
        evento_id, diretoria_id = _seed_evento_com_config_externa(s)
        user = _seed_npbb_user(s, email="npbb-desbloqueio-excesso@example.com")

        registrar_recebimento(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
            quantidade=120,
        )
        s.commit()

        auditoria, inv = desbloqueio_manual(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
            quantidade=10,
            usuario_id=int(user.id),
            motivo="Liberacao parcial do excedente",
        )
        s.commit()

        assert auditoria.bloqueado_antes == 20
        assert auditoria.bloqueado_depois == 10
        assert inv.bloqueado == 10
        assert inv.disponivel == 110

        override = s.exec(
            select(DesbloqueioManualInventario).where(
                DesbloqueioManualInventario.evento_id == evento_id,
                DesbloqueioManualInventario.diretoria_id == diretoria_id,
                DesbloqueioManualInventario.tipo_ingresso == TipoIngresso.PISTA,
            )
        ).first()
        assert override is not None
        assert override.tipo_bloqueio_atual.value == "excesso_recebido"
        assert override.quantidade_restante == 10

        recalculado = calcular_inventario(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
        )
        s.commit()
        assert recalculado.bloqueado == 10
        assert recalculado.disponivel == 110


def test_desbloqueio_manual_e_consumido_por_recebimento_real(engine):
    with Session(engine) as s:
        evento_id, diretoria_id = _seed_evento_com_config_externa(s)
        user = _seed_npbb_user(s, email="npbb-desbloqueio-consumo@example.com")

        registrar_recebimento(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
            quantidade=50,
        )
        s.commit()

        desbloqueio_manual(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
            quantidade=20,
            usuario_id=int(user.id),
            motivo="Cobertura temporaria",
        )
        s.commit()

        _, inv = registrar_recebimento(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
            quantidade=50,
        )
        s.commit()

        assert inv.recebido_confirmado == 100
        assert inv.bloqueado == 0
        assert inv.disponivel == 100

        override = s.exec(select(DesbloqueioManualInventario)).first()
        assert override is None


def test_desbloqueio_manual_e_consumido_por_aumento_de_previsao(engine):
    with Session(engine) as s:
        evento_id, diretoria_id = _seed_evento_com_config_externa(s)
        user = _seed_npbb_user(s, email="npbb-desbloqueio-previsao@example.com")

        registrar_recebimento(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
            quantidade=120,
        )
        s.commit()

        desbloqueio_manual(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
            quantidade=10,
            usuario_id=int(user.id),
            motivo="Uso excepcional do excedente",
        )
        s.commit()

        previsao = s.exec(
            select(PrevisaoIngresso).where(
                PrevisaoIngresso.evento_id == evento_id,
                PrevisaoIngresso.diretoria_id == diretoria_id,
                PrevisaoIngresso.tipo_ingresso == TipoIngresso.PISTA,
            )
        ).first()
        assert previsao is not None
        previsao.quantidade = 120
        s.add(previsao)
        s.flush()

        inv = calcular_inventario(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
        )
        s.commit()

        assert inv.bloqueado == 0
        assert inv.disponivel == 120

        override = s.exec(select(DesbloqueioManualInventario)).first()
        assert override is None


def test_desbloqueio_manual_modo_interno_levanta(engine):
    with Session(engine) as s:
        evento_id, diretoria_id = _seed_evento_com_config_externa(
            s,
            modo_fornecimento=ModoFornecimento.INTERNO_EMITIDO_COM_QR,
        )
        user = _seed_npbb_user(s, email="npbb-desbloqueio-interno@example.com")

        with pytest.raises(ValueError, match=MSG_DESBLOQUEIO_MODO_INVALIDO):
            desbloqueio_manual(
                s,
                evento_id=evento_id,
                diretoria_id=diretoria_id,
                tipo_ingresso=TipoIngresso.PISTA,
                quantidade=1,
                usuario_id=int(user.id),
                motivo="Nao deveria desbloquear",
            )


def test_desbloqueio_manual_quantidade_acima_do_bloqueado_levanta(engine):
    with Session(engine) as s:
        evento_id, diretoria_id = _seed_evento_com_config_externa(s)
        user = _seed_npbb_user(s, email="npbb-desbloqueio-limite@example.com")

        registrar_recebimento(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
            quantidade=50,
        )
        s.commit()

        with pytest.raises(ValueError, match=MSG_DESBLOQUEIO_EXCEDE_BLOQUEIO):
            desbloqueio_manual(
                s,
                evento_id=evento_id,
                diretoria_id=diretoria_id,
                tipo_ingresso=TipoIngresso.PISTA,
                quantidade=60,
                usuario_id=int(user.id),
                motivo="Excede saldo bloqueado",
            )


def test_desbloqueio_manual_sem_bloqueio_levanta(engine):
    with Session(engine) as s:
        evento_id, diretoria_id = _seed_evento_com_config_externa(s)
        user = _seed_npbb_user(s, email="npbb-desbloqueio-sem-bloqueio@example.com")

        registrar_recebimento(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
            quantidade=100,
        )
        s.commit()

        with pytest.raises(ValueError, match=MSG_DESBLOQUEIO_SEM_BLOQUEIO):
            desbloqueio_manual(
                s,
                evento_id=evento_id,
                diretoria_id=diretoria_id,
                tipo_ingresso=TipoIngresso.PISTA,
                quantidade=1,
                usuario_id=int(user.id),
                motivo="Sem bloqueio",
            )


def test_desbloqueio_manual_quantidade_invalida_levanta(engine):
    with Session(engine) as s:
        evento_id, diretoria_id = _seed_evento_com_config_externa(s)
        user = _seed_npbb_user(s, email="npbb-desbloqueio-qtd-invalida@example.com")

        with pytest.raises(ValueError, match=MSG_DESBLOQUEIO_QUANTIDADE_INVALIDA):
            desbloqueio_manual(
                s,
                evento_id=evento_id,
                diretoria_id=diretoria_id,
                tipo_ingresso=TipoIngresso.PISTA,
                quantidade=0,
                usuario_id=int(user.id),
                motivo="Quantidade invalida",
            )


def test_registrar_recebimento_modo_interno_levanta(engine):
    with Session(engine) as s:
        evento_id, diretoria_id = _seed_evento_com_config_externa(s)
        config = s.exec(
            select(ConfiguracaoIngressoEvento).where(
                ConfiguracaoIngressoEvento.evento_id == evento_id
            )
        ).first()
        assert config
        config.modo_fornecimento = ModoFornecimento.INTERNO_EMITIDO_COM_QR
        s.add(config)
        s.commit()

        with pytest.raises(ValueError, match="externo_recebido"):
            registrar_recebimento(
                s,
                evento_id=evento_id,
                diretoria_id=diretoria_id,
                tipo_ingresso=TipoIngresso.PISTA,
                quantidade=10,
            )


def test_calcular_inventario_modo_interno_sem_recebimentos(engine):
    with Session(engine) as s:
        evento_id, diretoria_id = _seed_evento_com_config_externa(s)
        config = s.exec(
            select(ConfiguracaoIngressoEvento).where(
                ConfiguracaoIngressoEvento.evento_id == evento_id
            )
        ).first()
        assert config
        config.modo_fornecimento = ModoFornecimento.INTERNO_EMITIDO_COM_QR
        s.add(config)
        s.commit()

        inv = calcular_inventario(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
        )
        s.commit()

        assert inv.planejado == 100
        assert inv.recebido_confirmado == 0
        assert inv.bloqueado == 0
        assert inv.disponivel == 100


def test_calcular_inventario_sem_previsao_resulta_planejado_zero(engine):
    with Session(engine) as s:
        evento_id, diretoria_id = _seed_evento_com_config_externa(s, previsao_quantidade=None)

        inv = calcular_inventario(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
        )
        s.commit()

        assert inv.planejado == 0
        assert inv.recebido_confirmado == 0
        assert inv.bloqueado == 0
        assert inv.disponivel == 0
        assert inv.distribuido == 0


def test_calcular_inventario_sem_configuracao_levanta(engine):
    with Session(engine) as s:
        with pytest.raises(ValueError, match="Configuracao de ingressos nao encontrada para o evento"):
            calcular_inventario(
                s,
                evento_id=999,
                diretoria_id=1,
                tipo_ingresso=TipoIngresso.PISTA,
            )


def test_calcular_inventario_tipo_inativo_levanta(engine):
    with Session(engine) as s:
        evento_id, diretoria_id = _seed_evento_com_config_externa(s)

        with pytest.raises(ValueError, match="Tipo de ingresso nao esta ativo para o evento"):
            calcular_inventario(
                s,
                evento_id=evento_id,
                diretoria_id=diretoria_id,
                tipo_ingresso=TipoIngresso.CAMAROTE,
            )


def test_calcular_inventario_ignora_distribuicoes_canceladas(engine):
    with Session(engine) as s:
        evento_id, diretoria_id = _seed_evento_com_config_externa(
            s,
            modo_fornecimento=ModoFornecimento.INTERNO_EMITIDO_COM_QR,
        )
        s.add(
            DistribuicaoIngresso(
                evento_id=evento_id,
                diretoria_id=diretoria_id,
                tipo_ingresso=TipoIngresso.PISTA,
                nome_destinatario="Pessoa Ativa",
                email_destinatario="ativa@example.com",
                status_destinatario=StatusDestinatario.ENVIADO,
            )
        )
        s.add(
            DistribuicaoIngresso(
                evento_id=evento_id,
                diretoria_id=diretoria_id,
                tipo_ingresso=TipoIngresso.PISTA,
                nome_destinatario="Pessoa Cancelada",
                email_destinatario="cancelada@example.com",
                status_destinatario=StatusDestinatario.CANCELADO,
            )
        )
        s.commit()

        inv = calcular_inventario(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
        )
        s.commit()

        assert inv.distribuido == 1
        assert inv.disponivel == 99


def test_calcular_inventario_recalculo_atualiza_mesmo_snapshot(engine):
    with Session(engine) as s:
        evento_id, diretoria_id = _seed_evento_com_config_externa(s)

        inv_inicial = calcular_inventario(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
        )
        s.commit()

        s.add(
            RecebimentoIngresso(
                evento_id=evento_id,
                diretoria_id=diretoria_id,
                tipo_ingresso=TipoIngresso.PISTA,
                quantidade=50,
            )
        )
        s.commit()

        inv_recalculado = calcular_inventario(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
        )
        s.commit()

        snapshots = s.exec(
            select(InventarioIngresso).where(
                InventarioIngresso.evento_id == evento_id,
                InventarioIngresso.diretoria_id == diretoria_id,
                InventarioIngresso.tipo_ingresso == TipoIngresso.PISTA,
            )
        ).all()

        assert inv_recalculado.id == inv_inicial.id
        assert inv_recalculado.recebido_confirmado == 50
        assert len(snapshots) == 1


def test_calcular_inventario_modo_interno_ignora_recebimentos_existentes(engine):
    with Session(engine) as s:
        evento_id, diretoria_id = _seed_evento_com_config_externa(
            s,
            modo_fornecimento=ModoFornecimento.INTERNO_EMITIDO_COM_QR,
        )
        s.add(
            RecebimentoIngresso(
                evento_id=evento_id,
                diretoria_id=diretoria_id,
                tipo_ingresso=TipoIngresso.PISTA,
                quantidade=80,
            )
        )
        s.commit()

        inv = calcular_inventario(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
        )
        s.commit()

        assert inv.planejado == 100
        assert inv.recebido_confirmado == 0
        assert inv.bloqueado == 0
        assert inv.disponivel == 100


def test_correlation_id_customizado(engine):
    with Session(engine) as s:
        evento_id, diretoria_id = _seed_evento_com_config_externa(s)
        cid = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        rec, _ = registrar_recebimento(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
            quantidade=1,
            correlation_id=cid,
        )
        s.commit()
        assert rec.correlation_id == cid

        loaded = s.exec(select(RecebimentoIngresso).where(RecebimentoIngresso.id == rec.id)).first()
        assert loaded is not None
        assert loaded.correlation_id == cid


def test_desbloqueio_manual_quantidade_none_desbloqueia_tudo(engine):
    """Quando quantidade=None, todo o saldo bloqueado e desbloqueado."""
    with Session(engine) as s:
        evento_id, diretoria_id = _seed_evento_com_config_externa(s)
        user = _seed_npbb_user(s, email="npbb-desbloqueio-total@example.com")

        registrar_recebimento(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
            quantidade=60,
        )
        s.commit()

        auditoria, inv = desbloqueio_manual(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
            quantidade=None,
            usuario_id=int(user.id),
            motivo="Desbloquear tudo",
        )
        s.commit()

        assert auditoria.quantidade == 40
        assert auditoria.bloqueado_antes == 40
        assert auditoria.bloqueado_depois == 0
        assert inv.bloqueado == 0
        assert inv.disponivel == 100

        override = s.exec(
            select(DesbloqueioManualInventario).where(
                DesbloqueioManualInventario.evento_id == evento_id,
            )
        ).first()
        assert override is not None
        assert override.quantidade_restante == 40


def test_desbloqueio_manual_aditivo_dois_consecutivos(engine):
    """Dois desbloqueios consecutivos acumulam no override persistido."""
    with Session(engine) as s:
        evento_id, diretoria_id = _seed_evento_com_config_externa(s)
        user = _seed_npbb_user(s, email="npbb-desbloqueio-aditivo@example.com")

        registrar_recebimento(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
            quantidade=50,
        )
        s.commit()

        _, inv1 = desbloqueio_manual(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
            quantidade=10,
            usuario_id=int(user.id),
            motivo="Primeiro desbloqueio parcial",
        )
        s.commit()
        assert inv1.bloqueado == 40
        assert inv1.disponivel == 60

        _, inv2 = desbloqueio_manual(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
            quantidade=15,
            usuario_id=int(user.id),
            motivo="Segundo desbloqueio parcial",
        )
        s.commit()
        assert inv2.bloqueado == 25
        assert inv2.disponivel == 75

        override = s.exec(
            select(DesbloqueioManualInventario).where(
                DesbloqueioManualInventario.evento_id == evento_id,
            )
        ).first()
        assert override is not None
        assert override.quantidade_restante == 25

        audits = s.exec(
            select(AuditoriaDesbloqueioInventario).where(
                AuditoriaDesbloqueioInventario.evento_id == evento_id,
            )
        ).all()
        assert len(audits) == 2


def test_desbloqueio_manual_cap_por_reducao_de_bloqueio_natural(engine):
    """Override e capado quando bloqueio natural diminui por novo recebimento parcial."""
    with Session(engine) as s:
        evento_id, diretoria_id = _seed_evento_com_config_externa(s)
        user = _seed_npbb_user(s, email="npbb-desbloqueio-cap@example.com")

        registrar_recebimento(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
            quantidade=50,
        )
        s.commit()

        desbloqueio_manual(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
            quantidade=40,
            usuario_id=int(user.id),
            motivo="Override grande",
        )
        s.commit()

        override_pre = s.exec(
            select(DesbloqueioManualInventario).where(
                DesbloqueioManualInventario.evento_id == evento_id,
            )
        ).first()
        assert override_pre is not None
        assert override_pre.quantidade_restante == 40

        _, inv = registrar_recebimento(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
            quantidade=30,
        )
        s.commit()

        # bloqueio_base now = 100-80 = 20; override capped from 40 to 20
        assert inv.recebido_confirmado == 80
        assert inv.bloqueado == 0
        assert inv.disponivel == 100

        override_post = s.exec(
            select(DesbloqueioManualInventario).where(
                DesbloqueioManualInventario.evento_id == evento_id,
            )
        ).first()
        assert override_post is not None
        assert override_post.quantidade_restante == 20

        # Another receipt closes the gap entirely; override is now cleaned
        _, inv2 = registrar_recebimento(
            s,
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            tipo_ingresso=TipoIngresso.PISTA,
            quantidade=20,
        )
        s.commit()

        assert inv2.recebido_confirmado == 100
        assert inv2.bloqueado == 0
        assert inv2.disponivel == 100

        override_final = s.exec(
            select(DesbloqueioManualInventario).where(
                DesbloqueioManualInventario.evento_id == evento_id,
            )
        ).first()
        assert override_final is None
