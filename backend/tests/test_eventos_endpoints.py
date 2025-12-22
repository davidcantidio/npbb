import csv
import io
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy.pool import StaticPool
from datetime import date
from decimal import Decimal

from app.db.database import get_session
from app.main import app
from app.models.models import (
    Agencia,
    Ativacao,
    CotaCortesia,
    DivisaoDemandante,
    Diretoria,
    Evento,
    FormularioLandingTemplate,
    FormularioLeadCampo,
    FormularioLeadConfig,
    StatusEvento,
    SubtipoEvento,
    Tag,
    Territorio,
    TipoEvento,
    Usuario,
)
from app.utils.security import hash_password


def make_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture
def engine(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "secret-test")
    engine = make_engine()
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        for nome in ["Previsto", "A Confirmar", "Confirmado", "Realizado", "Cancelado"]:
            exists = session.exec(select(StatusEvento).where(StatusEvento.nome == nome)).first()
            if not exists:
                session.add(StatusEvento(nome=nome))
        session.commit()
    return engine


@pytest.fixture
def client(engine):
    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def seed_agencia(session: Session, nome: str, dominio: str) -> Agencia:
    agencia = Agencia(nome=nome, dominio=dominio, lote=1)
    session.add(agencia)
    session.commit()
    session.refresh(agencia)
    return agencia


def seed_tipo(session: Session, nome: str = "Congresso") -> TipoEvento:
    tipo = TipoEvento(nome=nome)
    session.add(tipo)
    session.commit()
    session.refresh(tipo)
    return tipo


def seed_subtipo(session: Session, tipo: TipoEvento, nome: str = "Subtipo A") -> SubtipoEvento:
    subtipo = SubtipoEvento(tipo_id=tipo.id, nome=nome)
    session.add(subtipo)
    session.commit()
    session.refresh(subtipo)
    return subtipo


def seed_tag(session: Session, nome: str = "tag-a") -> Tag:
    tag = Tag(nome=nome)
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


def seed_territorio(session: Session, nome: str = "territorio-a") -> Territorio:
    territorio = Territorio(nome=nome)
    session.add(territorio)
    session.commit()
    session.refresh(territorio)
    return territorio


def seed_divisao(session: Session, nome: str = "Esportes") -> DivisaoDemandante:
    divisao = DivisaoDemandante(nome=nome)
    session.add(divisao)
    session.commit()
    session.refresh(divisao)
    return divisao


def seed_user(session: Session, email: str, password: str, tipo: str, agencia_id: int | None = None) -> Usuario:
    user = Usuario(
        email=email,
        password_hash=hash_password(password),
        tipo_usuario=tipo,
        agencia_id=agencia_id,
        ativo=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def login_and_get_token(client: TestClient, email: str, password: str) -> str:
    resp = client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def seed_evento(
    session: Session,
    *,
    agencia_id: int,
    tipo_id: int,
    nome: str,
    cidade: str,
    estado: str,
    inicio: date,
    fim: date,
    diretoria_id: int | None = None,
    status_nome: str = "Previsto",
) -> Evento:
    status = session.exec(select(StatusEvento).where(StatusEvento.nome == status_nome)).first()
    assert status and status.id
    evento = Evento(
        nome=nome,
        descricao="descricao",
        concorrencia=False,
        cidade=cidade,
        estado=estado,
        agencia_id=agencia_id,
        tipo_id=tipo_id,
        diretoria_id=diretoria_id,
        status_id=status.id,
        data_inicio_prevista=inicio,
        data_fim_prevista=fim,
    )
    session.add(evento)
    session.commit()
    session.refresh(evento)
    return evento


def seed_diretoria(session: Session, nome: str = "dimac") -> Diretoria:
    diretoria = Diretoria(nome=nome)
    session.add(diretoria)
    session.commit()
    session.refresh(diretoria)
    return diretoria


def test_evento_list_paginado_e_filtros(client, engine):
    with Session(engine) as session:
        ag1 = seed_agencia(session, "V3A", "v3a.com.br")
        tipo = seed_tipo(session)
        dir_a = seed_diretoria(session, "dimac")
        dir_b = seed_diretoria(session, "audit")
        dir_a_id = dir_a.id
        dir_b_id = dir_b.id
        user = seed_user(session, "user@example.com", "Senha123!", "npbb")

        seed_evento(
            session,
            agencia_id=ag1.id,
            tipo_id=tipo.id,
            diretoria_id=dir_a_id,
            nome="Evento Alpha",
            cidade="Sao Paulo",
            estado="SP",
            inicio=date(2025, 1, 1),
            fim=date(2025, 1, 2),
        )
        seed_evento(
            session,
            agencia_id=ag1.id,
            tipo_id=tipo.id,
            diretoria_id=dir_b_id,
            nome="Evento Beta",
            cidade="Rio de Janeiro",
            estado="RJ",
            inicio=date(2025, 2, 10),
            fim=date(2025, 2, 12),
        )
        seed_evento(
            session,
            agencia_id=ag1.id,
            tipo_id=tipo.id,
            nome="Outro",
            cidade="Sao Paulo",
            estado="SP",
            inicio=date(2025, 3, 1),
            fim=date(2025, 3, 1),
        )

    token = login_and_get_token(client, "user@example.com", "Senha123!")

    resp = client.get("/evento?limit=2", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.headers.get("X-Total-Count") == "3"
    assert len(resp.json()) == 2

    resp_sp = client.get("/evento?estado=sp", headers={"Authorization": f"Bearer {token}"})
    assert resp_sp.status_code == 200
    assert resp_sp.headers.get("X-Total-Count") == "2"

    resp_city = client.get("/evento?cidade=sao%20paulo", headers={"Authorization": f"Bearer {token}"})
    assert resp_city.status_code == 200
    assert resp_city.headers.get("X-Total-Count") == "2"

    resp_search = client.get("/evento?search=beta", headers={"Authorization": f"Bearer {token}"})
    assert resp_search.status_code == 200
    assert resp_search.headers.get("X-Total-Count") == "1"
    assert resp_search.json()[0]["nome"] == "Evento Beta"

    resp_date = client.get("/evento?data=2025-02-11", headers={"Authorization": f"Bearer {token}"})
    assert resp_date.status_code == 200
    assert resp_date.headers.get("X-Total-Count") == "1"
    assert resp_date.json()[0]["nome"] == "Evento Beta"

    resp_range = client.get(
        "/evento?data_inicio=2025-02-11&data_fim=2025-02-20",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_range.status_code == 200
    assert resp_range.headers.get("X-Total-Count") == "1"
    assert resp_range.json()[0]["nome"] == "Evento Beta"

    resp_bad_range = client.get(
        "/evento?data_inicio=2025-02-10&data_fim=2025-02-01",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_bad_range.status_code == 400
    detail = resp_bad_range.json()["detail"]
    assert detail["code"] == "DATE_RANGE_INVALID"

    resp_dir = client.get(f"/evento?diretoria_id={dir_a_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp_dir.status_code == 200
    assert resp_dir.headers.get("X-Total-Count") == "1"
    assert resp_dir.json()[0]["nome"] == "Evento Alpha"


def test_list_formulario_templates_ordenado(client, engine):
    with Session(engine) as session:
        session.add(FormularioLandingTemplate(nome="Surf", html_conteudo="<html></html>"))
        session.add(FormularioLandingTemplate(nome="BB Seguros", html_conteudo="<html></html>"))
        session.add(FormularioLandingTemplate(nome="Padrao", html_conteudo="<html></html>"))
        user = seed_user(session, "user2@example.com", "Senha123!", "npbb")
        session.commit()

    token = login_and_get_token(client, "user2@example.com", "Senha123!")
    resp = client.get("/evento/all/formulario-templates", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    nomes = [item["nome"] for item in resp.json()]
    assert nomes == sorted(nomes)


def test_evento_form_config_retorna_default_quando_nao_existe(client, engine):
    with Session(engine) as session:
        ag1 = seed_agencia(session, "V3A", "v3a.com.br")
        tipo = seed_tipo(session)
        seed_user(session, "user@example.com", "Senha123!", "npbb")
        evento = seed_evento(
            session,
            agencia_id=ag1.id,
            tipo_id=tipo.id,
            nome="Evento A",
            cidade="Sao Paulo",
            estado="SP",
            inicio=date(2025, 1, 1),
            fim=date(2025, 1, 1),
        )
        evento_id = evento.id

    token = login_and_get_token(client, "user@example.com", "Senha123!")
    resp = client.get(f"/evento/{evento_id}/form-config", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["evento_id"] == evento_id
    assert payload["template_id"] is None
    assert payload["campos"] == []
    assert payload["urls"]["url_landing"] == f"http://localhost:5173/landing/eventos/{evento_id}"
    assert payload["urls"]["url_promotor"] == f"http://localhost:5173/promotor/eventos/{evento_id}"
    assert payload["urls"]["url_questionario"] == f"http://localhost:5173/questionario/eventos/{evento_id}"
    assert payload["urls"]["url_api"] == "http://testserver/docs"
    assert "url_landing" not in payload


def test_evento_form_config_retorna_config_e_campos_ordenados(client, engine):
    with Session(engine) as session:
        ag1 = seed_agencia(session, "V3A", "v3a.com.br")
        tipo = seed_tipo(session)
        seed_user(session, "user@example.com", "Senha123!", "npbb")
        evento = seed_evento(
            session,
            agencia_id=ag1.id,
            tipo_id=tipo.id,
            nome="Evento A",
            cidade="Sao Paulo",
            estado="SP",
            inicio=date(2025, 1, 1),
            fim=date(2025, 1, 1),
        )
        evento_id = evento.id
        template = FormularioLandingTemplate(nome="Surf", html_conteudo="<html></html>")
        session.add(template)
        session.commit()
        session.refresh(template)
        template_id = template.id

        config = FormularioLeadConfig(
            evento_id=evento_id,
            nome="Config Landing",
            template_id=template_id,
            url_landing="https://example.com/landing",
            url_api="https://example.com/api",
        )
        session.add(config)
        session.commit()
        session.refresh(config)

        session.add(
            FormularioLeadCampo(
                config_id=config.id,
                nome_campo="Email",
                obrigatorio=True,
                ordem=2,
            )
        )
        session.add(
            FormularioLeadCampo(
                config_id=config.id,
                nome_campo="Nome",
                obrigatorio=True,
                ordem=1,
            )
        )
        session.commit()

    token = login_and_get_token(client, "user@example.com", "Senha123!")
    resp = client.get(f"/evento/{evento_id}/form-config", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["evento_id"] == evento_id
    assert payload["template_id"] == template_id
    assert [c["nome_campo"] for c in payload["campos"]] == ["Nome", "Email"]
    assert payload["urls"]["url_landing"] == "https://example.com/landing"
    assert payload["urls"]["url_api"] == "https://example.com/api"


def test_evento_form_config_aplica_visibilidade_agencia(client, engine):
    with Session(engine) as session:
        ag1 = seed_agencia(session, "V3A", "v3a.com.br")
        ag2 = seed_agencia(session, "Sherpa", "sherpa.com.br")
        tipo = seed_tipo(session)
        seed_user(session, "agencia@agencia.com.br", "Senha123!", "agencia", agencia_id=ag2.id)
        evento = seed_evento(
            session,
            agencia_id=ag1.id,
            tipo_id=tipo.id,
            nome="Evento A",
            cidade="Sao Paulo",
            estado="SP",
            inicio=date(2025, 1, 1),
            fim=date(2025, 1, 1),
        )
        evento_id = evento.id

    token = login_and_get_token(client, "agencia@agencia.com.br", "Senha123!")
    resp = client.get(f"/evento/{evento_id}/form-config", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404


def test_evento_put_form_config_cria_e_atualiza_template_id(client, engine):
    with Session(engine) as session:
        ag1 = seed_agencia(session, "V3A", "v3a.com.br")
        tipo = seed_tipo(session)
        seed_user(session, "user@example.com", "Senha123!", "npbb")
        evento = seed_evento(
            session,
            agencia_id=ag1.id,
            tipo_id=tipo.id,
            nome="Evento A",
            cidade="Sao Paulo",
            estado="SP",
            inicio=date(2025, 1, 1),
            fim=date(2025, 1, 1),
        )
        evento_id = evento.id

        template_a = FormularioLandingTemplate(nome="Surf", html_conteudo="<html></html>")
        template_b = FormularioLandingTemplate(nome="Padrao", html_conteudo="<html></html>")
        session.add(template_a)
        session.add(template_b)
        session.commit()
        session.refresh(template_a)
        session.refresh(template_b)

        template_a_id = template_a.id
        template_b_id = template_b.id

    token = login_and_get_token(client, "user@example.com", "Senha123!")

    resp_create = client.put(
        f"/evento/{evento_id}/form-config",
        json={"template_id": template_a_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_create.status_code == 200
    assert resp_create.json()["template_id"] == template_a_id

    with Session(engine) as session:
        configs = session.exec(select(FormularioLeadConfig).where(FormularioLeadConfig.evento_id == evento_id)).all()
        assert len(configs) == 1

    resp_update = client.put(
        f"/evento/{evento_id}/form-config",
        json={"template_id": template_b_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_update.status_code == 200
    assert resp_update.json()["template_id"] == template_b_id

    with Session(engine) as session:
        configs = session.exec(select(FormularioLeadConfig).where(FormularioLeadConfig.evento_id == evento_id)).all()
        assert len(configs) == 1
        assert configs[0].template_id == template_b_id


def test_evento_put_form_config_valida_template_id(client, engine):
    with Session(engine) as session:
        ag1 = seed_agencia(session, "V3A", "v3a.com.br")
        tipo = seed_tipo(session)
        seed_user(session, "user@example.com", "Senha123!", "npbb")
        evento = seed_evento(
            session,
            agencia_id=ag1.id,
            tipo_id=tipo.id,
            nome="Evento A",
            cidade="Sao Paulo",
            estado="SP",
            inicio=date(2025, 1, 1),
            fim=date(2025, 1, 1),
        )
        evento_id = evento.id

    token = login_and_get_token(client, "user@example.com", "Senha123!")
    resp = client.put(
        f"/evento/{evento_id}/form-config",
        json={"template_id": 9999},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400
    assert resp.json()["detail"]["code"] == "FORM_TEMPLATE_NOT_FOUND"


def test_evento_put_form_config_rejeita_campos_por_enquanto(client, engine):
    with Session(engine) as session:
        ag1 = seed_agencia(session, "V3A", "v3a.com.br")
        tipo = seed_tipo(session)
        seed_user(session, "user@example.com", "Senha123!", "npbb")
        evento = seed_evento(
            session,
            agencia_id=ag1.id,
            tipo_id=tipo.id,
            nome="Evento A",
            cidade="Sao Paulo",
            estado="SP",
            inicio=date(2025, 1, 1),
            fim=date(2025, 1, 1),
        )
        evento_id = evento.id

        template = FormularioLandingTemplate(nome="Surf", html_conteudo="<html></html>")
        session.add(template)
        session.commit()
        session.refresh(template)

    token = login_and_get_token(client, "user@example.com", "Senha123!")
    resp = client.put(
        f"/evento/{evento_id}/form-config",
        json={
            "template_id": template.id,
            "campos": [{"nome_campo": "Email", "obrigatorio": True, "ordem": 1}],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400
    assert resp.json()["detail"]["code"] == "FORM_CONFIG_FIELDS_NOT_SUPPORTED"


def test_evento_put_form_config_aplica_visibilidade_agencia(client, engine):
    with Session(engine) as session:
        ag1 = seed_agencia(session, "V3A", "v3a.com.br")
        ag2 = seed_agencia(session, "Sherpa", "sherpa.com.br")
        tipo = seed_tipo(session)
        seed_user(session, "agencia@agencia.com.br", "Senha123!", "agencia", agencia_id=ag2.id)
        evento = seed_evento(
            session,
            agencia_id=ag1.id,
            tipo_id=tipo.id,
            nome="Evento A",
            cidade="Sao Paulo",
            estado="SP",
            inicio=date(2025, 1, 1),
            fim=date(2025, 1, 1),
        )
        evento_id = evento.id

    token = login_and_get_token(client, "agencia@agencia.com.br", "Senha123!")
    resp = client.put(
        f"/evento/{evento_id}/form-config",
        json={"template_id": None},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


def test_evento_dicionarios_cidades_estados(client, engine):
    with Session(engine) as session:
        ag1 = seed_agencia(session, "V3A", "v3a.com.br")
        tipo = seed_tipo(session)
        seed_user(session, "user@example.com", "Senha123!", "npbb")
        seed_evento(
            session,
            agencia_id=ag1.id,
            tipo_id=tipo.id,
            nome="Evento A",
            cidade="Sao Paulo",
            estado="SP",
            inicio=date(2025, 1, 1),
            fim=date(2025, 1, 1),
        )
        seed_evento(
            session,
            agencia_id=ag1.id,
            tipo_id=tipo.id,
            nome="Evento B",
            cidade="Rio de Janeiro",
            estado="RJ",
            inicio=date(2025, 1, 2),
            fim=date(2025, 1, 2),
        )

    token = login_and_get_token(client, "user@example.com", "Senha123!")

    cities = client.get("/evento/all/cidades", headers={"Authorization": f"Bearer {token}"}).json()
    cities_sp = client.get("/evento/all/cidades?estado=sp", headers={"Authorization": f"Bearer {token}"}).json()
    states = client.get("/evento/all/estados", headers={"Authorization": f"Bearer {token}"}).json()
    assert "Sao Paulo" in cities
    assert "Rio de Janeiro" in cities
    assert cities_sp == ["Sao Paulo"]
    assert "SP" in states
    assert "RJ" in states


def test_evento_get_por_id_e_visibilidade_agencia(client, engine):
    with Session(engine) as session:
        ag1 = seed_agencia(session, "V3A", "v3a.com.br")
        ag2 = seed_agencia(session, "Sherpa", "sherpa.com.br")
        tipo = seed_tipo(session)

        evento_ag1 = seed_evento(
            session,
            agencia_id=ag1.id,
            tipo_id=tipo.id,
            nome="Evento A1",
            cidade="Sao Paulo",
            estado="SP",
            inicio=date(2025, 1, 1),
            fim=date(2025, 1, 1),
        )
        evento_ag2 = seed_evento(
            session,
            agencia_id=ag2.id,
            tipo_id=tipo.id,
            nome="Evento A2",
            cidade="Rio de Janeiro",
            estado="RJ",
            inicio=date(2025, 1, 2),
            fim=date(2025, 1, 2),
        )
        evento_ag1_id = evento_ag1.id
        evento_ag2_id = evento_ag2.id

        seed_user(session, "agencia@agencia.com.br", "Senha123!", "agencia", agencia_id=ag1.id)

    token = login_and_get_token(client, "agencia@agencia.com.br", "Senha123!")

    ok = client.get(f"/evento/{evento_ag1_id}", headers={"Authorization": f"Bearer {token}"})
    assert ok.status_code == 200
    assert ok.json()["id"] == evento_ag1_id

    forbidden = client.get(f"/evento/{evento_ag2_id}", headers={"Authorization": f"Bearer {token}"})
    assert forbidden.status_code == 404


def test_evento_criar_atualizar_e_excluir(client, engine):
    with Session(engine) as session:
        ag1 = seed_agencia(session, "V3A", "v3a.com.br")
        tipo = seed_tipo(session)
        div_a = seed_divisao(session, "Esportes")
        div_b = seed_divisao(session, "Agro")
        tag_a = seed_tag(session, "tag-a")
        tag_b = seed_tag(session, "tag-b")
        terr_a = seed_territorio(session, "Territorio A")
        terr_b = seed_territorio(session, "Territorio B")
        seed_user(session, "user@example.com", "Senha123!", "npbb")
        status_previsto = session.exec(select(StatusEvento).where(StatusEvento.nome == "Previsto")).first()
        status_cancelado = session.exec(select(StatusEvento).where(StatusEvento.nome == "Cancelado")).first()
        assert status_previsto and status_previsto.id
        assert status_cancelado and status_cancelado.id
        ag1_id = ag1.id
        tipo_id = tipo.id
        div_a_id = div_a.id
        div_b_id = div_b.id
        tag_a_id = tag_a.id
        tag_b_id = tag_b.id
        terr_a_id = terr_a.id
        terr_b_id = terr_b.id
        previsto_id = status_previsto.id
        cancelado_id = status_cancelado.id

    token = login_and_get_token(client, "user@example.com", "Senha123!")

    create_resp = client.post(
        "/evento",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "nome": "Evento Novo",
            "descricao": "descricao",
            "investimento": "100.00",
            "cidade": "Sao Paulo",
            "estado": "sp",
            "agencia_id": ag1_id,
            "tipo_id": tipo_id,
            "divisao_demandante_id": div_a_id,
            "data_inicio_prevista": "2099-01-01",
            "data_fim_prevista": "2099-01-02",
            "tag_ids": [tag_a_id],
            "territorio_ids": [terr_a_id],
        },
    )
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["id"]
    assert created["nome"] == "Evento Novo"
    assert created["estado"] == "SP"
    assert created["divisao_demandante_id"] == div_a_id
    assert Decimal(str(created["investimento"])) == Decimal("100.00")
    assert created["status_id"] == previsto_id
    assert created["tag_ids"] == [tag_a_id]
    assert created["territorio_ids"] == [terr_a_id]

    evento_id = created["id"]

    update_resp = client.put(
        f"/evento/{evento_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "cidade": "Rio de Janeiro",
            "estado": "rj",
            "divisao_demandante_id": div_b_id,
            "status_id": cancelado_id,
            "tag_ids": [tag_b_id],
            "territorio_ids": [terr_a_id, terr_b_id],
        },
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["cidade"] == "Rio de Janeiro"
    assert updated["estado"] == "RJ"
    assert updated["divisao_demandante_id"] == div_b_id
    assert updated["status_id"] == cancelado_id
    assert updated["tag_ids"] == [tag_b_id]
    assert updated["territorio_ids"] == sorted([terr_a_id, terr_b_id])

    delete_resp = client.delete(
        f"/evento/{evento_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_resp.status_code == 204

    get_resp = client.get(f"/evento/{evento_id}", headers={"Authorization": f"Bearer {token}"})
    assert get_resp.status_code == 404


def test_evento_delete_bloqueado_por_dependencias(client, engine):
    with Session(engine) as session:
        ag1 = seed_agencia(session, "V3A", "v3a.com.br")
        tipo = seed_tipo(session)
        seed_user(session, "user@example.com", "Senha123!", "npbb")

        evento = seed_evento(
            session,
            agencia_id=ag1.id,
            tipo_id=tipo.id,
            nome="Evento Bloqueado",
            cidade="Sao Paulo",
            estado="SP",
            inicio=date(2025, 1, 1),
            fim=date(2025, 1, 1),
        )
        evento_id = evento.id
        ativacao = Ativacao(
            nome="Ativacao",
            descricao="desc",
            evento_id=evento_id,
            valor=Decimal("10.00"),
        )
        session.add(ativacao)
        session.commit()

    token = login_and_get_token(client, "user@example.com", "Senha123!")
    resp = client.delete(f"/evento/{evento_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 409
    detail = resp.json()["detail"]
    assert detail["code"] == "EVENTO_DELETE_BLOCKED"
    assert "ativacoes" in detail["dependencies"]


def test_evento_all_dominios(client, engine):
    with Session(engine) as session:
        seed_user(session, "user@example.com", "Senha123!", "npbb")
        diretoria_a = seed_diretoria(session, "dimac")
        diretoria_b = seed_diretoria(session, "audit")
        diretoria_a_id = diretoria_a.id
        diretoria_b_id = diretoria_b.id
        divisao_a = seed_divisao(session, "Esportes")
        divisao_b = seed_divisao(session, "Agro")
        divisao_a_id = divisao_a.id
        divisao_b_id = divisao_b.id

        tipo_a = seed_tipo(session, "Congresso")
        tipo_b = seed_tipo(session, "Feira")
        subtipo_a1 = seed_subtipo(session, tipo_a, "Sub A1")
        subtipo_b1 = seed_subtipo(session, tipo_b, "Sub B1")
        tipo_a_id = tipo_a.id
        tipo_b_id = tipo_b.id
        subtipo_a1_id = subtipo_a1.id
        subtipo_b1_id = subtipo_b1.id

        tag_a = seed_tag(session, "tag-a")
        tag_b = seed_tag(session, "tag-b")
        terr_a = seed_territorio(session, "Territorio A")
        terr_b = seed_territorio(session, "Territorio B")
        tag_a_id = tag_a.id
        tag_b_id = tag_b.id
        terr_a_id = terr_a.id
        terr_b_id = terr_b.id

    token = login_and_get_token(client, "user@example.com", "Senha123!")
    headers = {"Authorization": f"Bearer {token}"}

    diretorias = client.get("/evento/all/diretorias", headers=headers).json()
    assert any(d["id"] == diretoria_a_id for d in diretorias)
    assert any(d["id"] == diretoria_b_id for d in diretorias)

    divisoes = client.get("/evento/all/divisoes-demandantes", headers=headers).json()
    assert any(d["id"] == divisao_a_id for d in divisoes)
    assert any(d["id"] == divisao_b_id for d in divisoes)

    tipos = client.get("/evento/all/tipos-evento", headers=headers).json()
    assert any(t["id"] == tipo_a_id for t in tipos)
    assert any(t["id"] == tipo_b_id for t in tipos)

    subtipos = client.get(f"/evento/all/subtipos-evento?tipo_id={tipo_a_id}", headers=headers).json()
    assert any(s["id"] == subtipo_a1_id for s in subtipos)
    assert all(s["tipo_id"] == tipo_a_id for s in subtipos)
    assert not any(s["id"] == subtipo_b1_id for s in subtipos)

    territorios = client.get("/evento/all/territorios", headers=headers).json()
    assert any(t["id"] == terr_a_id for t in territorios)
    assert any(t["id"] == terr_b_id for t in territorios)

    tags = client.get("/evento/all/tags", headers=headers).json()
    assert any(t["id"] == tag_a_id for t in tags)
    assert any(t["id"] == tag_b_id for t in tags)

    diretorias_search = client.get("/evento/all/diretorias?search=aud", headers=headers).json()
    assert any(d["id"] == diretoria_b_id for d in diretorias_search)

    statuses = client.get("/evento/all/status-evento", headers=headers).json()
    assert any(s["nome"] == "Previsto" for s in statuses)


def test_evento_criar_tag_dinamica(client, engine):
    with Session(engine) as session:
        seed_user(session, "user@example.com", "Senha123!", "npbb")

    token = login_and_get_token(client, "user@example.com", "Senha123!")
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/evento/tags", headers=headers, json={"nome": "Nova Tag"})
    assert resp.status_code == 201
    tag = resp.json()
    assert tag["id"]
    assert tag["nome"] == "Nova Tag"

    resp_2 = client.post("/evento/tags", headers=headers, json={"nome": "Nova Tag"})
    assert resp_2.status_code == 200
    assert resp_2.json()["id"] == tag["id"]


def test_evento_export_csv_respeita_visibilidade_agencia(client, engine):
    with Session(engine) as session:
        ag1 = seed_agencia(session, "V3A", "v3a.com.br")
        ag2 = seed_agencia(session, "Sherpa", "sherpa.com.br")
        tipo = seed_tipo(session)
        ag1_id = ag1.id

        e1 = seed_evento(
            session,
            agencia_id=ag1.id,
            tipo_id=tipo.id,
            nome="Evento A1",
            cidade="Sao Paulo",
            estado="SP",
            inicio=date(2025, 1, 1),
            fim=date(2025, 1, 1),
        )
        e1_id = e1.id
        seed_evento(
            session,
            agencia_id=ag2.id,
            tipo_id=tipo.id,
            nome="Evento A2",
            cidade="Rio de Janeiro",
            estado="RJ",
            inicio=date(2025, 1, 2),
            fim=date(2025, 1, 2),
        )

        seed_user(session, "agencia@agencia.com.br", "Senha123!", "agencia", agencia_id=ag1.id)

    token = login_and_get_token(client, "agencia@agencia.com.br", "Senha123!")
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/evento/export/csv", headers=headers)
    assert resp.status_code == 200
    assert "text/csv" in resp.headers.get("content-type", "")
    assert "eventos.csv" in resp.headers.get("content-disposition", "")

    text = resp.content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text), delimiter=";")
    rows = list(reader)
    assert rows
    assert ag1_id is not None
    assert e1_id is not None
    assert all(int(row["agencia_id"]) == ag1_id for row in rows)
    assert any(int(row["id"]) == e1_id for row in rows)
