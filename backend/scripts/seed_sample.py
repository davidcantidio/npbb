"""
Seed de dados de desenvolvimento (Supabase) para popular dominios basicos.

- Agencias (4)
- Diretorias (lista)
- Templates de landing (temas)
- Tipos/Subtipos de evento (dominios)
- Territorios (dominios)
- Usuarios: npbb, bb (com funcionario), agencia (associado a agencia V3A)

Variaveis de ambiente:
- DATABASE_URL / DIRECT_URL: conexao Postgres (Supabase). Para seed, usamos DIRECT_URL se existir.
- SECRET_KEY: exigido pelo util de JWT, mas aqui so usamos hash de senha.
- SEED_PASSWORD: senha para todos os usuarios criados (padrao: "Senha123!").
"""

import os
import time
from decimal import Decimal
from pathlib import Path

from sqlmodel import Session, create_engine, select
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError

# Garante que o pacote app seja encontrado quando o script eh executado diretamente
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in os.sys.path:
    os.sys.path.insert(0, str(BASE_DIR))

from app.models.models import (  # noqa: E402
    Agencia,
    Ativacao,
    Diretoria,
    DivisaoDemandante,
    Evento,
    FormularioLandingTemplate,
    Funcionario,
    Gamificacao,
    SubtipoEvento,
    Territorio,
    TipoEvento,
    Usuario,
    UsuarioTipo,
)
from app.utils.security import hash_password  # noqa: E402


PASSWORD = os.getenv("SEED_PASSWORD", "Senha123!")


def _load_env() -> None:
    """Carrega .env priorizando `backend/.env` e caindo para `.env` na raiz do repo."""
    candidate_paths = [
        BASE_DIR / ".env",  # backend/.env
        BASE_DIR.parent / ".env",  # npbb/.env
    ]
    for env_path in candidate_paths:
        if env_path.exists():
            load_dotenv(env_path)
            return
    load_dotenv()


def _build_seed_engine():
    echo = os.getenv("SQL_ECHO", "false").lower() == "true"
    connect_timeout = int(os.getenv("SEED_CONNECT_TIMEOUT", "10"))

    direct_url = os.getenv("DIRECT_URL")
    database_url = os.getenv("DATABASE_URL")

    candidates: list[tuple[str, str]] = []
    if direct_url:
        candidates.append(("DIRECT_URL", direct_url))
    if database_url and database_url != direct_url:
        candidates.append(("DATABASE_URL", database_url))
    if not candidates:
        raise RuntimeError("DIRECT_URL/DATABASE_URL nao configuradas.")

    last_error: Exception | None = None
    for label, url in candidates:
        engine = create_engine(url, echo=echo, connect_args={"connect_timeout": connect_timeout})
        for attempt in range(1, 4):
            try:
                with engine.connect() as conn:
                    # força a abertura da conexao antes de iniciar o seed
                    conn.exec_driver_sql("SELECT 1")
                print(f"Conectado ao banco via {label}.")
                return engine
            except OperationalError as exc:
                last_error = exc
                wait_seconds = attempt * 2
                print(
                    f"Aviso: falha ao conectar via {label} (tentativa {attempt}/3). "
                    f"Tentando novamente em {wait_seconds}s..."
                )
                time.sleep(wait_seconds)

        print(f"Aviso: nao foi possivel conectar via {label}. Tentando proxima URL...")

    raise last_error or RuntimeError("Nao foi possivel conectar ao banco para executar o seed.")


def ensure_agencias(session: Session) -> dict[str, Agencia]:
    entries = [
        ("V3A", 1),
        ("Sherpa", 1),
        ("Monumenta", 2),
        ("Terrua", 2),
    ]
    result: dict[str, Agencia] = {}
    for nome, lote in entries:
        agencia = session.exec(select(Agencia).where(Agencia.nome == nome)).first()
        dominio_slug = "".join(nome.lower().split())
        dominio = f"{dominio_slug}.com.br"
        if not agencia:
            agencia = Agencia(nome=nome, dominio=dominio, lote=lote)
            session.add(agencia)
            session.commit()
            session.refresh(agencia)
        elif not agencia.dominio or "." not in agencia.dominio:
            agencia.dominio = dominio
            session.add(agencia)
            session.commit()
            session.refresh(agencia)
        result[nome] = agencia
    return result


def ensure_diretorias(session: Session) -> dict[str, Diretoria]:
    nomes = [
        "audit",
        "bb_consorcios",
        "bb_previdencia",
        "bb_seguros",
        "cenop",
        "clients_mpe",
        "clinicassi",
        "coger",
        "crm",
        "dicoi",
        "dicor",
        "dicre",
        "diemp",
        "difin",
        "digov",
        "dimac",
        "dimep",
        "dined",
        "diope",
        "dipes",
        "direc",
        "direo",
        "diris",
        "disec",
        "ditec",
        "dijur",
        "divar",
        "gecor",
        "gecem",
        "gepes",
        "qvt",
        "reunioes",
        "secex",
        "super_adm",
        "uac",
        "uan",
        "uci",
        "ucf",
        "uni_corp_bank",
        "usi",
        "uri",
    ]
    result: dict[str, Diretoria] = {}
    for nome in nomes:
        diretoria = session.exec(select(Diretoria).where(Diretoria.nome == nome)).first()
        if not diretoria:
            diretoria = Diretoria(nome=nome)
            session.add(diretoria)
            session.commit()
            session.refresh(diretoria)
        result[nome] = diretoria
    return result


def ensure_divisoes_demandantes(session: Session) -> dict[str, DivisaoDemandante]:
    nomes = [
        "Esportes",
        "Agro",
        "Sustentabilidade/TI",
        "Cultura e Entretenimento",
    ]
    result: dict[str, DivisaoDemandante] = {}
    for nome in nomes:
        divisao = session.exec(select(DivisaoDemandante).where(DivisaoDemandante.nome == nome)).first()
        if not divisao:
            divisao = DivisaoDemandante(nome=nome)
            session.add(divisao)
            session.commit()
            session.refresh(divisao)
        result[nome] = divisao
    return result


def ensure_tipos_subtipos_evento(session: Session) -> dict[str, TipoEvento]:
    mapping: dict[str, list[str]] = {
        "Esporte": [
            "Vôlei de quadra",
            "Vôlei de praia",
            "Corrida de rua",
            "Surfe",
            "Skate",
            "Canoagem",
        ],
        "Cultura": [
            "Feira",
            "Encontro",
            "Convenção",
            "Festival",
        ],
        "Entretenimento": [
            "Feira",
            "Festival",
            "Show musical",
            "Teatro",
        ],
        "Inovação": [
            "Feira",
            "Simpósio",
            "Congresso",
            "Encontro",
            "Hackathon",
            "Palestra",
        ],
    }

    tipos: dict[str, TipoEvento] = {}
    for tipo_nome in mapping.keys():
        tipo = session.exec(select(TipoEvento).where(TipoEvento.nome == tipo_nome)).first()
        if not tipo:
            tipo = TipoEvento(nome=tipo_nome)
            session.add(tipo)
            session.commit()
            session.refresh(tipo)
        tipos[tipo_nome] = tipo

    for tipo_nome, subtipos in mapping.items():
        tipo = tipos[tipo_nome]
        for subtipo_nome in subtipos:
            exists = session.exec(
                select(SubtipoEvento).where(
                    SubtipoEvento.tipo_id == tipo.id,
                    SubtipoEvento.nome == subtipo_nome,
                )
            ).first()
            if exists:
                continue
            session.add(SubtipoEvento(tipo_id=tipo.id, nome=subtipo_nome))
        session.commit()

    return tipos


def ensure_territorios(session: Session) -> dict[str, Territorio]:
    nomes = [
        "Tecnologia",
        "Esporte",
        "Sustentabilidade (ASG)",
        "Agro",
    ]
    result: dict[str, Territorio] = {}
    for nome in nomes:
        territorio = session.exec(select(Territorio).where(Territorio.nome == nome)).first()
        if not territorio:
            territorio = Territorio(nome=nome)
            session.add(territorio)
            session.commit()
            session.refresh(territorio)
        result[nome] = territorio
    return result


def ensure_formulario_templates(session: Session) -> dict[str, FormularioLandingTemplate]:
    templates: dict[str, dict[str, str | None]] = {
        "Surf": {
            "html": "<html><body><h1>Template Surf</h1><p>Placeholder (MVP).</p></body></html>",
            "css": "body{font-family:Arial,sans-serif;background:#f5f7fb}h1{color:#1e88e5}",
        },
        "Padrão": {
            "html": "<html><body><h1>Template Padrão</h1><p>Placeholder (MVP).</p></body></html>",
            "css": "body{font-family:Arial,sans-serif;background:#ffffff}h1{color:#4a148c}",
        },
        "BB Seguros": {
            "html": "<html><body><h1>Template BB Seguros</h1><p>Placeholder (MVP).</p></body></html>",
            "css": "body{font-family:Arial,sans-serif;background:#ffffff}h1{color:#0d47a1}",
        },
    }

    result: dict[str, FormularioLandingTemplate] = {}
    for nome, conteudo in templates.items():
        template = session.exec(select(FormularioLandingTemplate).where(FormularioLandingTemplate.nome == nome)).first()
        if not template:
            template = FormularioLandingTemplate(
                nome=nome,
                html_conteudo=str(conteudo["html"]),
                css_conteudo=conteudo["css"],
            )
            session.add(template)
            session.commit()
            session.refresh(template)
        else:
            changed = False
            if not template.html_conteudo:
                template.html_conteudo = str(conteudo["html"])
                changed = True
            if template.css_conteudo is None and conteudo["css"] is not None:
                template.css_conteudo = str(conteudo["css"])
                changed = True
            if changed:
                session.add(template)
                session.commit()
                session.refresh(template)
        result[nome] = template
    return result


def ensure_funcionario_dimac(session: Session, diretoria_dimac: Diretoria) -> Funcionario:
    funcionario = session.exec(
        select(Funcionario).where(Funcionario.email == "funcionario@bb.com.br")
    ).first()
    if funcionario:
        return funcionario
    funcionario = Funcionario(
        nome="Funcionario BB",
        chave_c="CHV-BB-001",
        diretoria_id=diretoria_dimac.id,
        email="funcionario@bb.com.br",
        telefone=None,
    )
    session.add(funcionario)
    session.commit()
    session.refresh(funcionario)
    return funcionario


def ensure_usuario(
    session: Session,
    email: str,
    tipo: UsuarioTipo,
    password: str,
    funcionario_id: int | None = None,
    agencia_id: int | None = None,
    nome_info: str | None = None,
) -> Usuario:
    usuario = session.exec(select(Usuario).where(Usuario.email == email)).first()
    if usuario:
        return usuario
    usuario = Usuario(
        email=email,
        password_hash=hash_password(password),
        tipo_usuario=tipo,
        funcionario_id=funcionario_id,
        agencia_id=agencia_id,
        ativo=True,
    )
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    if nome_info:
        print(f"Usuario criado: {nome_info} ({email})")
    return usuario


def ensure_ativacoes_sample(session: Session, *, agencia_ids: list[int]) -> int:
    """Cria 2-3 ativações de exemplo por evento (idempotente).

    Regras (MVP):
    - sempre cria 2 ativações sem gamificação
    - cria 1 ativação com gamificação (se existir gamificação cadastrada no evento)
    """

    eventos = session.exec(
        select(Evento).where(Evento.agencia_id.in_(agencia_ids)).order_by(Evento.id)
    ).all()
    if not eventos:
        print("Nenhum evento encontrado para criar ativações de exemplo.")
        return 0

    created = 0
    for evento in eventos:
        if not evento.id:
            continue
        created_event = 0

        gamificacao = session.exec(
            select(Gamificacao).where(Gamificacao.evento_id == evento.id).order_by(Gamificacao.id)
        ).first()

        samples: list[dict[str, object]] = [
            {
                "nome": "Ativacao - Check-in",
                "descricao": "Ativacao de exemplo (check-in unico).",
                "mensagem_qrcode": "Check-in valido apenas uma vez.",
                "checkin_unico": True,
            },
            {
                "nome": "Ativacao - Cupom",
                "descricao": "Ativacao de exemplo (gera cupom).",
                "mensagem_qrcode": "Cupom gerado apos o check-in.",
                "gera_cupom": True,
                "termo_uso": True,
            },
        ]

        if gamificacao and gamificacao.id:
            samples.append(
                {
                    "nome": "Ativacao - Gamificacao",
                    "descricao": "Ativacao de exemplo vinculada a uma gamificacao.",
                    "mensagem_qrcode": "Valide para participar da gamificacao.",
                    "gamificacao_id": gamificacao.id,
                }
            )

        for sample in samples:
            nome = str(sample["nome"])
            exists = session.exec(
                select(Ativacao).where(Ativacao.evento_id == evento.id, Ativacao.nome == nome)
            ).first()
            if exists:
                continue

            ativacao = Ativacao(
                evento_id=evento.id,
                nome=nome,
                descricao=str(sample.get("descricao") or ""),
                mensagem_qrcode=str(sample.get("mensagem_qrcode") or ""),
                gamificacao_id=sample.get("gamificacao_id"),
                redireciona_pesquisa=bool(sample.get("redireciona_pesquisa", False)),
                checkin_unico=bool(sample.get("checkin_unico", False)),
                termo_uso=bool(sample.get("termo_uso", False)),
                gera_cupom=bool(sample.get("gera_cupom", False)),
                valor=Decimal("0.00"),
            )
            session.add(ativacao)
            created_event += 1

        if created_event:
            session.commit()
            created += created_event

    if created:
        print(f"Ativacoes de exemplo criadas: {created}.")
    else:
        print("Ativacoes de exemplo ja existiam; nada a criar.")
    return created


def main():
    _load_env()
    engine = _build_seed_engine()
    with Session(engine) as session:
        agencias = ensure_agencias(session)
        diretorias = ensure_diretorias(session)
        ensure_formulario_templates(session)
        ensure_divisoes_demandantes(session)
        ensure_tipos_subtipos_evento(session)
        ensure_territorios(session)

        func_dimac = ensure_funcionario_dimac(session, diretorias["dimac"])

        ensure_usuario(
            session,
            email="david.cantidio@npbb.com.br",
            tipo=UsuarioTipo.NPBB,
            password=PASSWORD,
            nome_info="David (NPBB)",
        )
        ensure_usuario(
            session,
            email="funcionario@bb.com.br",
            tipo=UsuarioTipo.BB,
            password=PASSWORD,
            funcionario_id=func_dimac.id,
            nome_info="Funcionario BB (dimac)",
        )
        ensure_usuario(
            session,
            email="agencia@agencia.com.br",
            tipo=UsuarioTipo.AGENCIA,
            password=PASSWORD,
            agencia_id=agencias["V3A"].id,
            nome_info="Usuario Agencia (V3A)",
        )

        ensure_ativacoes_sample(session, agencia_ids=[a.id for a in agencias.values() if a.id])

    print("Seed de desenvolvimento concluido.")
    print(f"Senha usada: {PASSWORD!r}")


if __name__ == "__main__":
    main()
