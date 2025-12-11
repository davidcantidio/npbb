import os
import sys
from pathlib import Path

from sqlmodel import Session, select
from dotenv import load_dotenv

# Garante que o pacote app seja encontrado quando o script é executado diretamente
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.db.database import engine, init_db  # noqa: E402
from app.models.models import Usuario, UsuarioTipo  # noqa: E402
from app.utils.security import hash_password  # noqa: E402


def get_env_or_exit(key: str) -> str:
    value = os.getenv(key)
    if not value:
        print(f"Erro: variável de ambiente {key} não definida.")
        sys.exit(1)
    return value


def main() -> None:
    load_dotenv(BASE_DIR / ".env")

    email = get_env_or_exit("ADMIN_EMAIL")
    password = get_env_or_exit("ADMIN_PASSWORD")
    tipo_raw = os.getenv("ADMIN_TIPO", "npbb").lower()

    try:
        tipo = UsuarioTipo(tipo_raw)
    except ValueError:
        print(f"Tipo inválido '{tipo_raw}', usando 'npbb'.")
        tipo = UsuarioTipo.NPBB

    init_db()
    with Session(engine) as session:
        existing = session.exec(select(Usuario).where(Usuario.email == email)).first()
        if existing:
            print(f"Usuário admin já existe: {email}")
            return

        usuario = Usuario(
            email=email,
            password_hash=hash_password(password),
            tipo_usuario=tipo,
            ativo=True,
        )
        session.add(usuario)
        session.commit()
        session.refresh(usuario)
        print(f"Usuário admin criado: {usuario.email} (id={usuario.id})")


if __name__ == "__main__":
    main()
