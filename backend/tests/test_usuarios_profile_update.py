from __future__ import annotations

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.models.models import Diretoria, Funcionario, Usuario, UsuarioTipo
from app.routers.usuarios import atualizar_perfil_bb
from app.schemas.usuario import UsuarioPerfilUpdate


def make_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def test_atualizar_perfil_bb_reaproveita_funcionario_existente_por_email() -> None:
    engine = make_engine()
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        diretoria_antiga = Diretoria(nome="DIRETORIA-ANTIGA")
        diretoria_nova = Diretoria(nome="DIRETORIA-NOVA")
        session.add(diretoria_antiga)
        session.add(diretoria_nova)
        session.commit()
        session.refresh(diretoria_antiga)
        session.refresh(diretoria_nova)

        funcionario = Funcionario(
            nome="funcionario",
            chave_c="c0001",
            diretoria_id=int(diretoria_antiga.id),
            email="funcionario@bb.com.br",
        )
        session.add(funcionario)
        session.commit()
        session.refresh(funcionario)

        usuario = Usuario(
            email="funcionario@bb.com.br",
            password_hash="hashed",
            tipo_usuario=UsuarioTipo.BB,
            ativo=True,
        )
        session.add(usuario)
        session.commit()
        session.refresh(usuario)

        payload = UsuarioPerfilUpdate(matricula="C9999", diretoria_id=int(diretoria_nova.id))
        response = atualizar_perfil_bb(payload=payload, session=session, current_user=usuario)

        funcionarios = session.exec(select(Funcionario)).all()
        assert len(funcionarios) == 1

        session.refresh(funcionario)
        session.refresh(usuario)

        assert funcionario.id == usuario.funcionario_id
        assert funcionario.chave_c == "c9999"
        assert funcionario.diretoria_id == int(diretoria_nova.id)
        assert response.funcionario_id == funcionario.id
        assert usuario.status_aprovacao == "APROVADO"
