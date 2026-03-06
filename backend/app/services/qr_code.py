"""Geracao de QR Code em SVG/data URL."""

from __future__ import annotations

import base64
from html import escape
from io import BytesIO


def build_qr_code_svg(content: str) -> str:
    value = str(content or "").strip()
    if not value:
        raise ValueError("QR code requer conteudo nao vazio")

    try:
        import qrcode
        import qrcode.image.svg

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(value)
        qr.make(fit=True)
        image = qr.make_image(image_factory=qrcode.image.svg.SvgPathImage)
        buffer = BytesIO()
        image.save(buffer)
        return buffer.getvalue().decode("utf-8")
    except Exception:
        escaped = escape(value)
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" width="320" height="320" viewBox="0 0 320 320" '
            'role="img" aria-label="QR Code alternativo">'
            '<rect width="320" height="320" rx="24" fill="#3333BD"/>'
            '<rect x="20" y="20" width="280" height="280" rx="20" fill="#FCFC30"/>'
            '<text x="160" y="120" text-anchor="middle" font-size="34" font-family="Arial, sans-serif" '
            'font-weight="700" fill="#3333BD">QR</text>'
            '<text x="160" y="155" text-anchor="middle" font-size="18" font-family="Arial, sans-serif" '
            'fill="#3333BD">Acesse a landing</text>'
            f'<text x="160" y="205" text-anchor="middle" font-size="12" font-family="Arial, sans-serif" '
            f'fill="#3333BD">{escaped[:40]}</text>'
            "</svg>"
        )


def build_qr_code_data_url(content: str) -> str:
    svg = build_qr_code_svg(content)
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"
