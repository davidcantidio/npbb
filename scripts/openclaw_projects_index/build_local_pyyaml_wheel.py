#!/usr/bin/env python3
"""Builds a local pure-Python PyYAML wheel from the installed package."""

from __future__ import annotations

import argparse
import base64
import hashlib
from pathlib import Path
import zipfile

try:
    import yaml
except ModuleNotFoundError as exc:  # pragma: no cover - explicit runtime failure path.
    raise SystemExit("PyYAML precisa estar instalado localmente para exportar o wheel do deploy.") from exc


def add_wheel_file(zf: zipfile.ZipFile, records: list[str], arcname: str, data: bytes) -> None:
    digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).decode("ascii").rstrip("=")
    records.append(f"{arcname},sha256={digest},{len(data)}")
    zf.writestr(arcname, data)


def pinned_yaml_version(requirements_path: Path) -> str:
    for line in requirements_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("PyYAML=="):
            return line.split("==", 1)[1].strip()
    raise SystemExit(f"Não foi possível ler o pin de PyYAML em {requirements_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Exporta um wheel local do PyYAML já instalado.")
    parser.add_argument("--output-dir", required=True, help="Diretório de saída do wheelhouse.")
    args = parser.parse_args()

    here = Path(__file__).resolve().parent
    requirements_path = here / "requirements.txt"
    expected_version = pinned_yaml_version(requirements_path)
    installed_version = getattr(yaml, "__version__", "")
    if installed_version != expected_version:
        raise SystemExit(
            f"PyYAML local fora do pin esperado: requirements={expected_version} instalado={installed_version}"
        )

    package_dir = Path(yaml.__file__).resolve().parent
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    dist_info = f"PyYAML-{installed_version}.dist-info"
    wheel_path = output_dir / f"PyYAML-{installed_version}-py3-none-any.whl"

    metadata = "\n".join(
        [
            "Metadata-Version: 2.1",
            "Name: PyYAML",
            f"Version: {installed_version}",
            "Summary: Local wheel exported for OpenClaw projects index bootstrap",
            "",
        ]
    ).encode("utf-8")
    wheel = "\n".join(
        [
            "Wheel-Version: 1.0",
            "Generator: build_local_pyyaml_wheel.py",
            "Root-Is-Purelib: true",
            "Tag: py3-none-any",
            "",
        ]
    ).encode("utf-8")
    top_level = b"yaml\n"

    records: list[str] = []
    with zipfile.ZipFile(wheel_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(package_dir.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            arcname = path.relative_to(package_dir.parent).as_posix()
            add_wheel_file(zf, records, arcname, path.read_bytes())

        add_wheel_file(zf, records, f"{dist_info}/METADATA", metadata)
        add_wheel_file(zf, records, f"{dist_info}/WHEEL", wheel)
        add_wheel_file(zf, records, f"{dist_info}/top_level.txt", top_level)
        records.append(f"{dist_info}/RECORD,,")
        zf.writestr(f"{dist_info}/RECORD", "\n".join(records).encode("utf-8"))

    print(wheel_path)


if __name__ == "__main__":
    main()
