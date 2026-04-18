#!/usr/bin/env python3
"""Benchmark leve para Task 5: contagem streaming de CSV Gold e pico de RSS opcional.

Uso (a partir da raiz do repo):
  python backend/scripts/benchmark_lead_import_task5.py --rows 5000
  python backend/scripts/benchmark_lead_import_task5.py --rows 20000 --csv /caminho/consolidado.csv

Requer: stdlib; `psutil` opcional para RSS (pip install psutil).
"""

from __future__ import annotations

import argparse
import csv
import io
import os
import tempfile
import time
from pathlib import Path


def _try_rss() -> tuple[int | None, str]:
    try:
        import psutil  # type: ignore[import-untyped]

        rss = int(psutil.Process(os.getpid()).memory_info().rss)
        return rss, "psutil"
    except Exception:
        return None, "unavailable"


def _write_synthetic_consolidated_csv(path: Path, n_data_rows: int) -> None:
    fieldnames = ["cpf", "email", "nome", "evento", "source_file", "source_sheet", "source_row"]
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        for i in range(n_data_rows):
            cpf = f"{(i % 10_000):011d}"[:11]
            w.writerow(
                {
                    "cpf": cpf,
                    "email": f"user{i}@bench.npbb",
                    "nome": f"Bench {i}",
                    "evento": "Bench Evento",
                    "source_file": "bench.csv",
                    "source_sheet": "",
                    "source_row": str(i + 2),
                }
            )


def count_rows_streaming(path: Path) -> int:
    with path.open(encoding="utf-8") as fh:
        r = csv.reader(fh)
        next(r, None)  # header
        return sum(1 for _ in r)


def count_rows_materialized(path: Path) -> int:
    with path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
        return len(rows)


def main() -> None:
    p = argparse.ArgumentParser(description="Benchmark Task 5 import / Gold CSV")
    p.add_argument("--rows", type=int, default=5000, help="Linhas de dados (sem header)")
    p.add_argument("--csv", type=Path, default=None, help="CSV existente; senao gera temporario")
    args = p.parse_args()

    rss0, rss_src = _try_rss()
    if args.csv is not None:
        csv_path = args.csv
        cleanup: Path | None = None
    else:
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8")
        tmp.close()
        csv_path = Path(tmp.name)
        cleanup = csv_path
        _write_synthetic_consolidated_csv(csv_path, args.rows)

    try:
        t0 = time.perf_counter()
        n_stream = count_rows_streaming(csv_path)
        t_stream_ms = (time.perf_counter() - t0) * 1000

        t1 = time.perf_counter()
        n_mat = count_rows_materialized(csv_path)
        t_mat_ms = (time.perf_counter() - t1) * 1000

        rss1, _ = _try_rss()
    finally:
        if cleanup is not None:
            cleanup.unlink(missing_ok=True)

    print(f"csv={csv_path}")
    print(f"rows_streaming={n_stream} time_ms={t_stream_ms:.2f}")
    print(f"rows_materialized={n_mat} time_ms={t_mat_ms:.2f}")
    print(f"rss_tool={rss_src} rss_before={rss0} rss_after_materialized={rss1}")
    if n_stream != n_mat:
        raise SystemExit(f"Mismatch row counts: {n_stream} != {n_mat}")


if __name__ == "__main__":
    main()
