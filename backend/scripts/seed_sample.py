"""
Seed de dados de desenvolvimento (Supabase) para popular dominios basicos.

- Agencias (4)
- Diretorias (lista)
- Usuarios: npbb, bb (com funcionario), agencia (associado a agencia V3A)

Variaveis de ambiente:
- DATABASE_URL / DIRECT_URL: conexao Postgres (Supabase).
- SECRET_KEY: exigido pelo util de JWT, mas aqui so usamos hash de senha.
- SEED_PASSWORD: senha para todos os usuarios criados (padrao: "Senha123!").
"""

import os
from pathlib import Path

from sqlmodel import Session, select
from dotenv import load_dotenv

# Garante que o pacote app seja encontrado quando o script eh executado diretamente
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in os.sys.path:
    os.sys.path.insert(0, str(BASE_DIR))

from app.db.database import engine  # noqa: E402
from app.models.models import Agencia, Diretoria, Funcionario, Usuario, UsuarioTipo  # noqa: E402
from app.utils.security import hash_password  # noqa: E402


PASSWORD = os.getenv("SEED_PASSWORD", "Senha123!")


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


def main():
    load_dotenv(BASE_DIR / ".env")
    with Session(engine) as session:
        agencias = ensure_agencias(session)
        diretorias = ensure_diretorias(session)

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

    print("Seed de desenvolvimento concluido.")
    print(f"Senha usada: {PASSWORD!r}")


if __name__ == "__main__":
    main()
