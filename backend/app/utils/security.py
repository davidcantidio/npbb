"""Utilitários de segurança para hashing e verificação de senha."""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Gera o hash seguro para uma senha em texto plano."""
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    """Valida uma senha em texto plano contra um hash existente."""
    return pwd_context.verify(plain, hashed)
