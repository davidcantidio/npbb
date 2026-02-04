import time

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.models.models import Usuario
from app.utils.security import hash_password


def make_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def test_updated_at_changes_on_update():
    engine = make_engine()
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        usuario = Usuario(
            email="user@npbb.com.br",
            password_hash=hash_password("senha123"),
            tipo_usuario="npbb",
        )
        session.add(usuario)
        session.commit()
        session.refresh(usuario)
        first_updated_at = usuario.updated_at

        time.sleep(0.001)
        usuario.ativo = False
        session.add(usuario)
        session.commit()
        session.refresh(usuario)

        assert usuario.updated_at > first_updated_at
