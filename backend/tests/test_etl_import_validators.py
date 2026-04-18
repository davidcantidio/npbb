from __future__ import annotations

import pytest

from app.modules.leads_publicidade.application.etl_import.validators import (
    INVALID_CPF_REASON,
    MALFORMED_EMAIL_REASON,
    MISSING_CPF_REASON,
    is_valid_cpf,
    is_valid_email,
    validate_normalized_lead_payload,
)


@pytest.mark.parametrize(
    "email",
    [
        "lead@example.com",
        "lead.name+tag@sub.example.com",
        "a@b.co",
    ],
)
def test_is_valid_email_accepts_basic_normalized_email(email: str) -> None:
    assert is_valid_email(email) is True


@pytest.mark.parametrize(
    "email",
    [
        "leadexample.com",
        "lead@localhost",
        "lead@example",
        "lead @example.com",
        "lead@example .com",
        "",
        None,
    ],
)
def test_is_valid_email_rejects_malformed_or_missing_email(email: object) -> None:
    assert is_valid_email(email) is False


@pytest.mark.parametrize(
    "cpf",
    [
        "52998224725",
        "11144477735",
        "10000000019",
    ],
)
def test_is_valid_cpf_accepts_valid_normalized_cpf(cpf: str) -> None:
    assert is_valid_cpf(cpf) is True


@pytest.mark.parametrize(
    "cpf",
    [
        "52998224726",
        "11111111111",
        "12345678909",
        "12345678901",
        "5299822472",
        "529982247250",
        "529.982.247-25",
        "",
        None,
    ],
)
def test_is_valid_cpf_rejects_invalid_or_not_normalized_cpf(cpf: object) -> None:
    assert is_valid_cpf(cpf) is False


def test_validate_normalized_lead_payload_allows_missing_optional_email() -> None:
    assert validate_normalized_lead_payload({"email": None, "cpf": "52998224725"}) == []
    assert validate_normalized_lead_payload({"cpf": "52998224725"}) == []


def test_validate_normalized_lead_payload_reports_reasons_in_deterministic_order() -> None:
    assert validate_normalized_lead_payload(
        {"email": "lead example.com", "cpf": "11111111111"}
    ) == [
        MALFORMED_EMAIL_REASON,
        INVALID_CPF_REASON,
    ]


def test_validate_normalized_lead_payload_reports_missing_cpf_when_absent() -> None:
    assert validate_normalized_lead_payload({"email": "ok@example.com", "cpf": None}) == [MISSING_CPF_REASON]
    assert validate_normalized_lead_payload({"email": "ok@example.com", "cpf": ""}) == [MISSING_CPF_REASON]


def test_validate_normalized_lead_payload_invalid_cpf_digits_when_present() -> None:
    assert validate_normalized_lead_payload({"email": "ok@example.com", "cpf": "12345678901"}) == [
        INVALID_CPF_REASON
    ]


def test_validate_normalized_lead_payload_rejects_known_placeholder_cpf_sequence() -> None:
    assert validate_normalized_lead_payload({"email": "ok@example.com", "cpf": "12345678909"}) == [
        INVALID_CPF_REASON
    ]
