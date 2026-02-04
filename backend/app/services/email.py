"""Servico simples de envio de email.

Suporta dois backends:
- console (padrao): imprime o email no stdout (bom para dev/testes).
- smtp: envia via SMTP com as variaveis SMTP_*.
"""

from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage


def send_email(to: str, subject: str, body: str) -> None:
    backend = os.getenv("EMAIL_BACKEND", "console").lower().strip()

    if backend == "console":
        print("\n=== EMAIL (console) ===")
        print(f"To: {to}")
        print(f"Subject: {subject}")
        print(body)
        print("=== END EMAIL ===\n")
        return

    if backend != "smtp":
        raise ValueError("EMAIL_BACKEND invalido. Use 'console' ou 'smtp'.")

    host = os.getenv("SMTP_HOST")
    if not host:
        raise RuntimeError("SMTP_HOST nao configurado (EMAIL_BACKEND=smtp).")

    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    from_addr = os.getenv("SMTP_FROM") or user
    if not from_addr:
        raise RuntimeError("SMTP_FROM (ou SMTP_USER) nao configurado (EMAIL_BACKEND=smtp).")

    use_tls = os.getenv("SMTP_TLS", "true").lower() == "true"
    use_ssl = os.getenv("SMTP_SSL", "false").lower() == "true"

    msg = EmailMessage()
    msg["To"] = to
    msg["From"] = from_addr
    msg["Subject"] = subject
    msg.set_content(body)

    if use_ssl:
        with smtplib.SMTP_SSL(host, port) as server:
            if user and password:
                server.login(user, password)
            server.send_message(msg)
        return

    with smtplib.SMTP(host, port) as server:
        server.ehlo()
        if use_tls:
            server.starttls()
            server.ehlo()
        if user and password:
            server.login(user, password)
        server.send_message(msg)
