import pytest

from app.utils.security import hash_password, verify_password


def test_hash_and_verify_password():
    plain = "senha-segura"
    hashed = hash_password(plain)

    assert hashed != plain
    assert verify_password(plain, hashed) is True


def test_verify_password_fails_for_wrong_input():
    plain = "senha-segura"
    hashed = hash_password(plain)

    assert verify_password("errada", hashed) is False
