from datetime import date, datetime, timedelta, timezone

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.models.models import Agencia, Evento, Lead, LeadReconhecimentoToken, StatusEvento, TipoEvento
from app.services.reconhecimento import (
    LEAD_RECOGNITION_TTL_DAYS,
    gerar_token,
    validar_token,
)


def make_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _normalize_utc(dt: datetime) -> datetime:
    if getattr(dt, "tzinfo", None) is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def seed_agencia(session: Session) -> Agencia:
    agencia = Agencia(nome="V3A", dominio="v3a.com.br", lote=1)
    session.add(agencia)
    session.commit()
    session.refresh(agencia)
    return agencia


def seed_tipo(session: Session) -> TipoEvento:
    tipo = TipoEvento(nome="Congresso")
    session.add(tipo)
    session.commit()
    session.refresh(tipo)
    return tipo


def seed_status(session: Session) -> StatusEvento:
    status = StatusEvento(nome="Previsto")
    session.add(status)
    session.commit()
    session.refresh(status)
    return status


def seed_evento(session: Session) -> Evento:
    agencia = seed_agencia(session)
    tipo = seed_tipo(session)
    status = seed_status(session)
    evento = Evento(
        nome="Evento Reconhecimento",
        descricao="Evento de teste.",
        concorrencia=False,
        cidade="Brasilia",
        estado="DF",
        agencia_id=agencia.id,
        tipo_id=tipo.id,
        status_id=status.id,
        data_inicio_prevista=date(2026, 4, 10),
        data_fim_prevista=date(2026, 4, 12),
    )
    session.add(evento)
    session.commit()
    session.refresh(evento)
    return evento


def seed_lead(session: Session, *, evento_nome: str) -> Lead:
    lead = Lead(
        nome="Maria",
        email="maria@example.com",
        cpf="52998224725",
        evento_nome=evento_nome,
        cidade="Brasilia",
        estado="DF",
        fonte_origem="landing_publica",
        opt_in="aceito",
        opt_in_flag=True,
    )
    session.add(lead)
    session.commit()
    session.refresh(lead)
    return lead


def test_gerar_token_persiste_hash_e_ttl(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "secret-test")
    engine = make_engine()
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        evento = seed_evento(session)
        lead = seed_lead(session, evento_nome=evento.nome)
        before = datetime.now(timezone.utc)

        token = gerar_token(session, lead_id=lead.id, evento_id=evento.id)

        record = session.exec(select(LeadReconhecimentoToken)).one()
        expires_delta = _normalize_utc(record.expires_at) - before

        assert token
        assert record.token_hash != token
        assert record.token_hash
        assert record.lead_id == lead.id
        assert record.evento_id == evento.id
        assert timedelta(days=LEAD_RECOGNITION_TTL_DAYS) - timedelta(seconds=5) <= expires_delta
        assert expires_delta <= timedelta(days=LEAD_RECOGNITION_TTL_DAYS, seconds=5)


def test_validar_token_retorna_lead_quando_token_valido(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "secret-test")
    engine = make_engine()
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        evento = seed_evento(session)
        lead = seed_lead(session, evento_nome=evento.nome)
        token = gerar_token(session, lead_id=lead.id, evento_id=evento.id)
        session.commit()

        result = validar_token(session, token=token, evento_id=evento.id)

        assert result is not None
        assert result.lead_id == lead.id
        assert result.evento_id == evento.id


def test_validar_token_retorna_none_quando_expirado_ou_evento_diverge(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "secret-test")
    engine = make_engine()
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        evento = seed_evento(session)
        outro_evento = Evento(
            nome="Outro Evento",
            descricao="Outro.",
            concorrencia=False,
            cidade="Brasilia",
            estado="DF",
            agencia_id=evento.agencia_id,
            tipo_id=evento.tipo_id,
            status_id=evento.status_id,
            data_inicio_prevista=date(2026, 4, 20),
            data_fim_prevista=date(2026, 4, 21),
        )
        session.add(outro_evento)
        session.commit()
        session.refresh(outro_evento)

        lead = seed_lead(session, evento_nome=evento.nome)
        token = gerar_token(session, lead_id=lead.id, evento_id=evento.id)
        session.commit()

        record = session.exec(select(LeadReconhecimentoToken)).one()
        record.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        session.add(record)
        session.commit()

        assert validar_token(session, token=token, evento_id=evento.id) is None
        assert validar_token(session, token=token, evento_id=outro_evento.id) is None
