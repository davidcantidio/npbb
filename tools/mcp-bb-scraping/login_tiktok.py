from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any
import requests


class LoginError(RuntimeError):
    pass


@dataclass
class CookieLoginResult:
    session: requests.Session
    user_info: Optional[Dict[str, Any]] = None


def login_with_cookie(
    base_url: str,
    cookie_name: str,
    cookie_value: str,
    *,
    verify_url: str = "/me",          # endpoint que só funciona logado
    cookie_domain: Optional[str] = None,
    cookie_path: str = "/",
    timeout: float = 15.0,
    headers: Optional[Dict[str, str]] = None,
) -> CookieLoginResult:
    """
    Reusa um cookie de autenticação para "logar" via HTTP.

    Use APENAS cookies de uma sessão sua e autorizada.
    """
    base_url = base_url.rstrip("/")
    verify_full_url = verify_url if verify_url.startswith("http") else f"{base_url}{verify_url}"

    s = requests.Session()

    # Headers opcionais (às vezes o serviço exige User-Agent, etc.)
    if headers:
        s.headers.update(headers)

    # Define o cookie na sessão
    s.cookies.set(
        name=cookie_name,
        value=cookie_value,
        domain=cookie_domain,  # se der 401, tente None ou o domínio exato (ex: "api.exemplo.com")
        path=cookie_path,
    )

    # Faz uma requisição a um endpoint que confirme autenticação
    r = s.get(verify_full_url, timeout=timeout)
    if r.status_code in (401, 403):
        raise LoginError(
            f"Cookie não autenticou (HTTP {r.status_code}). "
            f"Talvez expirou, domínio/path não batem, ou falta CSRF/headers."
        )
    r.raise_for_status()

    # Tenta parsear JSON, se existir
    try:
        data = r.json()
    except ValueError:
        data = None

    return CookieLoginResult(session=s, user_info=data)


# Exemplo de uso:
if __name__ == "__main__":
    result = login_with_cookie(
        base_url="https://api.exemplo.com",
        cookie_name="sessionid",
        cookie_value="96db33d447c8f054cd221e3b43ab9737",
        verify_url="/me",
        headers={"User-Agent": "scriptzinho-sem-vergonha/1.0"},
    )

    print("Logado. /me =", result.user_info)
    # Agora você usa result.session para chamadas autenticadas:
    # resp = result.session.get("https://api.exemplo.com/pedidos")
