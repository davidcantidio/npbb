from app.utils.log_sanitize import sanitize_exception, sanitize_text


def test_sanitize_text_masks_common_pii() -> None:
    raw = "Email Test.User@BB.com.br CPF 123.456.789-10 tel (11) 91234-5678 token 1234567890123"
    sanitized = sanitize_text(raw)

    assert "Test.User@BB.com.br" not in sanitized
    assert "123.456.789-10" not in sanitized
    assert "91234-5678" not in sanitized
    assert "1234567890123" not in sanitized
    assert len(sanitized) <= 300


def test_sanitize_exception_includes_type() -> None:
    exc = ValueError("email usuario@bb.com.br cpf 12345678901")
    sanitized = sanitize_exception(exc)

    assert sanitized.startswith("ValueError")
    assert "usuario@bb.com.br" not in sanitized
    assert "12345678901" not in sanitized
