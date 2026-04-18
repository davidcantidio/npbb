import csv
from contextlib import nullcontext
from pathlib import Path

import pytest

from app.services import lead_pipeline_service


class _FakeLead:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.id = None


class _FakeSession:
    def __init__(self, bind=None):
        self.commits = 0
        self.flushes = 0
        self._next_id = 1
        self._bind = bind

    def add(self, _obj):
        return None

    def flush(self):
        self.flushes += 1

    def commit(self):
        self.commits += 1

    def get_bind(self):
        return self._bind

    def begin_nested(self):
        return nullcontext()

    def exec(self, _stmt):
        class _ExecResult:
            def all(self_inner):
                return []

            def first(self_inner):
                return None

        return _ExecResult()


class _FakeDialect:
    name = "postgresql"


class _FakeBind:
    def __init__(self, url: str | None = None):
        self.url = url
        self.dialect = _FakeDialect()


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["nome", "cpf", "email"])
        writer.writeheader()
        writer.writerows(rows)


def test_inserir_leads_gold_commits_in_batches(monkeypatch, tmp_path):
    csv_path = tmp_path / "gold.csv"
    _write_csv(
        csv_path,
        [
            {"nome": "A", "cpf": "1", "email": "a@example.com"},
            {"nome": "B", "cpf": "2", "email": "b@example.com"},
            {"nome": "C", "cpf": "3", "email": "c@example.com"},
        ],
    )

    fake_db = _FakeSession()
    fake_batch = type(
        "FakeBatch",
        (),
        {
            "id": 54,
            "origem_lote": "proponente",
            "ativacao_id": None,
            "tipo_lead_proponente": "entrada_evento",
            "evento_id": None,
            "plataforma_origem": "drive",
        },
    )()

    def _fake_build_payload(row, _batch):
        return dict(row)

    def _fake_find_existing_lead(_db, _payload, anchored_evento_id=None):
        return None

    def _fake_flush(self):
        self.flushes += 1

    timeout_calls: list[str] = []
    progress_events: list[tuple[str, str, int | None]] = []

    monkeypatch.setenv("LEAD_GOLD_INSERT_COMMIT_BATCH_SIZE", "2")
    monkeypatch.setattr(lead_pipeline_service, "_configure_lead_gold_statement_timeout", lambda _db: timeout_calls.append("timeout"))
    monkeypatch.setattr(lead_pipeline_service, "_build_lead_payload", _fake_build_payload)
    monkeypatch.setattr(lead_pipeline_service, "_find_existing_lead", _fake_find_existing_lead)
    monkeypatch.setattr(lead_pipeline_service, "Lead", _FakeLead)

    created = lead_pipeline_service._inserir_leads_gold(
        fake_batch,
        csv_path,
        fake_db,
        on_progress=lambda event: progress_events.append((event.step, event.label, event.pct)),
    )

    assert created == 3
    assert fake_db.flushes == 3
    assert fake_db.commits == 2
    assert timeout_calls == ["timeout", "timeout"]
    assert progress_events == [
        ("insert_leads", "Inserindo leads Gold no banco (0/3)", 0),
        ("insert_leads", "Inserindo leads Gold no banco (2/3)", 66),
        ("insert_leads", "Inserindo leads Gold no banco (3/3)", 100),
    ]


def test_inserir_leads_gold_emits_heartbeat_progress_before_final_commit(monkeypatch, tmp_path):
    csv_path = tmp_path / "gold-heartbeat.csv"
    _write_csv(
        csv_path,
        [
            {"nome": "A", "cpf": "1", "email": "a@example.com"},
            {"nome": "B", "cpf": "2", "email": "b@example.com"},
            {"nome": "C", "cpf": "3", "email": "c@example.com"},
        ],
    )

    fake_db = _FakeSession()
    fake_batch = type(
        "FakeBatch",
        (),
        {
            "id": 55,
            "origem_lote": "proponente",
            "ativacao_id": None,
            "tipo_lead_proponente": "entrada_evento",
            "evento_id": None,
            "plataforma_origem": "drive",
        },
    )()

    def _fake_build_payload(row, _batch):
        return dict(row)

    def _fake_find_existing_lead(_db, _payload, anchored_evento_id=None):
        return None

    perf_counter_values = iter([0.0, 5.0, 26.0, 30.0, 31.0])
    timeout_calls: list[str] = []
    progress_events: list[tuple[str, str, int | None]] = []

    monkeypatch.setenv("LEAD_GOLD_INSERT_COMMIT_BATCH_SIZE", "5")
    monkeypatch.setenv("LEAD_GOLD_PROGRESS_HEARTBEAT_SECONDS", "20")
    monkeypatch.setattr(
        lead_pipeline_service.time_module,
        "perf_counter",
        lambda: next(perf_counter_values, 31.0),
    )
    monkeypatch.setattr(lead_pipeline_service, "_configure_lead_gold_statement_timeout", lambda _db: timeout_calls.append("timeout"))
    monkeypatch.setattr(lead_pipeline_service, "_build_lead_payload", _fake_build_payload)
    monkeypatch.setattr(lead_pipeline_service, "_find_existing_lead", _fake_find_existing_lead)
    monkeypatch.setattr(lead_pipeline_service, "Lead", _FakeLead)

    created = lead_pipeline_service._inserir_leads_gold(
        fake_batch,
        csv_path,
        fake_db,
        on_progress=lambda event: progress_events.append((event.step, event.label, event.pct)),
    )

    assert created == 3
    assert fake_db.flushes == 3
    assert fake_db.commits == 1
    assert timeout_calls == ["timeout"]
    assert progress_events == [
        ("insert_leads", "Inserindo leads Gold no banco (0/3)", 0),
        ("insert_leads", "Inserindo leads Gold no banco (1/3)", 33),
        ("insert_leads", "Inserindo leads Gold no banco (3/3)", 100),
    ]


def test_lead_gold_insert_commit_batch_size_caps_supabase_transaction_pooler(monkeypatch):
    fake_db = _FakeSession(
        bind=_FakeBind("postgresql+psycopg2://u:p@aws-0-xx.pooler.supabase.com:6543/postgres")
    )

    monkeypatch.setenv("LEAD_GOLD_INSERT_COMMIT_BATCH_SIZE", "100")
    monkeypatch.delenv("LEAD_GOLD_INSERT_COMMIT_BATCH_SIZE_SUPABASE_POOLER_6543", raising=False)

    assert lead_pipeline_service._lead_gold_insert_commit_batch_size(fake_db) == 25


def test_inserir_leads_gold_commits_early_on_supabase_transaction_budget(monkeypatch, tmp_path):
    csv_path = tmp_path / "gold-time-budget.csv"
    _write_csv(
        csv_path,
        [
            {"nome": "A", "cpf": "1", "email": "a@example.com"},
            {"nome": "B", "cpf": "2", "email": "b@example.com"},
            {"nome": "C", "cpf": "3", "email": "c@example.com"},
        ],
    )

    fake_db = _FakeSession(
        bind=_FakeBind("postgresql+psycopg2://u:p@aws-0-xx.pooler.supabase.com:6543/postgres")
    )
    fake_batch = type(
        "FakeBatch",
        (),
        {
            "id": 56,
            "origem_lote": "proponente",
            "ativacao_id": None,
            "tipo_lead_proponente": "entrada_evento",
            "evento_id": None,
            "plataforma_origem": "drive",
        },
    )()

    def _fake_build_payload(row, _batch):
        return dict(row)

    def _fake_find_existing_lead(_db, _payload, anchored_evento_id=None):
        return None

    perf_counter_values = iter([0.0, 1.0, 11.0, 12.0, 12.0, 13.0])
    progress_events: list[tuple[str, str, int | None]] = []
    timeout_calls: list[str] = []

    monkeypatch.setenv("LEAD_GOLD_INSERT_COMMIT_BATCH_SIZE", "100")
    monkeypatch.setenv("LEAD_GOLD_INSERT_COMMIT_BATCH_SIZE_SUPABASE_POOLER_6543", "25")
    monkeypatch.setenv("LEAD_GOLD_INSERT_MAX_TRANSACTION_SECONDS_SUPABASE_POOLER_6543", "10")
    monkeypatch.setenv("LEAD_GOLD_PROGRESS_HEARTBEAT_SECONDS", "20")
    monkeypatch.setattr(
        lead_pipeline_service.time_module,
        "perf_counter",
        lambda: next(perf_counter_values, 13.0),
    )
    monkeypatch.setattr(
        lead_pipeline_service,
        "_configure_lead_gold_statement_timeout",
        lambda _db: timeout_calls.append("timeout"),
    )
    monkeypatch.setattr(lead_pipeline_service, "_build_lead_payload", _fake_build_payload)
    monkeypatch.setattr(lead_pipeline_service, "_find_existing_lead", _fake_find_existing_lead)
    monkeypatch.setattr(lead_pipeline_service, "Lead", _FakeLead)

    created = lead_pipeline_service._inserir_leads_gold(
        fake_batch,
        csv_path,
        fake_db,
        on_progress=lambda event: progress_events.append((event.step, event.label, event.pct)),
    )

    assert created == 3
    assert fake_db.flushes == 3
    assert fake_db.commits == 2
    assert timeout_calls == ["timeout", "timeout"]
    assert progress_events == [
        ("insert_leads", "Inserindo leads Gold no banco (0/3)", 0),
        ("insert_leads", "Inserindo leads Gold no banco (1/3)", 33),
        ("insert_leads", "Inserindo leads Gold no banco (3/3)", 100),
    ]


def test_inserir_leads_gold_raises_for_missing_consolidated_file(tmp_path):
    fake_db = _FakeSession()
    fake_batch = type(
        "FakeBatch",
        (),
        {
            "id": 54,
            "origem_lote": "proponente",
            "ativacao_id": None,
            "tipo_lead_proponente": "entrada_evento",
            "evento_id": None,
            "plataforma_origem": "drive",
        },
    )()

    with pytest.raises(FileNotFoundError, match="CSV consolidado da pipeline Gold nao encontrado"):
        lead_pipeline_service._inserir_leads_gold(fake_batch, tmp_path / "missing.csv", fake_db)


def test_inserir_leads_gold_raises_for_empty_consolidated_file(tmp_path):
    csv_path = tmp_path / "gold-empty.csv"
    csv_path.write_text("nome,cpf,email\n", encoding="utf-8")

    fake_db = _FakeSession()
    fake_batch = type(
        "FakeBatch",
        (),
        {
            "id": 54,
            "origem_lote": "proponente",
            "ativacao_id": None,
            "tipo_lead_proponente": "entrada_evento",
            "evento_id": None,
            "plataforma_origem": "drive",
        },
    )()

    with pytest.raises(ValueError, match="CSV consolidado da pipeline Gold vazio"):
        lead_pipeline_service._inserir_leads_gold(fake_batch, csv_path, fake_db)


def test_inserir_leads_gold_ignores_resume_when_content_hash_differs(monkeypatch, tmp_path):
    csv_path = tmp_path / "gold-resume-hash-mismatch.csv"
    _write_csv(
        csv_path,
        [
            {"nome": "A", "cpf": "1", "email": "a@example.com"},
            {"nome": "B", "cpf": "2", "email": "b@example.com"},
            {"nome": "C", "cpf": "3", "email": "c@example.com"},
        ],
    )

    fake_db = _FakeSession()
    fake_batch = type(
        "FakeBatch",
        (),
        {
            "id": 57,
            "origem_lote": "proponente",
            "ativacao_id": None,
            "tipo_lead_proponente": "entrada_evento",
            "evento_id": None,
            "plataforma_origem": "drive",
            "arquivo_sha256": "a" * 64,
        },
    )()

    def _fake_build_payload(row, _batch):
        return dict(row)

    def _fake_find_existing_lead(_db, _payload, anchored_evento_id=None):
        return None

    progress_events: list[tuple[str, str, int | None]] = []

    monkeypatch.setenv("LEAD_GOLD_INSERT_COMMIT_BATCH_SIZE", "10")
    monkeypatch.setattr(lead_pipeline_service, "_build_lead_payload", _fake_build_payload)
    monkeypatch.setattr(lead_pipeline_service, "_find_existing_lead", _fake_find_existing_lead)
    monkeypatch.setattr(lead_pipeline_service, "Lead", _FakeLead)

    created = lead_pipeline_service._inserir_leads_gold(
        fake_batch,
        csv_path,
        fake_db,
        on_progress=lambda event: progress_events.append((event.step, event.label, event.pct)),
        resume_context={
            "step": "insert_leads",
            "committed_rows": 2,
            "total_rows": 3,
            "content_hash": "f" * 64,
            "arquivo_sha256": "a" * 64,
        },
    )

    assert created == 3
    assert progress_events[0] == ("insert_leads", "Inserindo leads Gold no banco (0/3)", 0)


def test_inserir_leads_gold_loads_lookup_in_fixed_windows(monkeypatch, tmp_path):
    csv_path = tmp_path / "gold-lookup-window.csv"
    rows = [
        {
            "nome": f"Lead {idx}",
            "cpf": f"{idx + 1:011d}",
            "email": f"lead{idx}@example.com",
        }
        for idx in range(120)
    ]
    _write_csv(csv_path, rows)

    fake_db = _FakeSession()
    fake_batch = type(
        "FakeBatch",
        (),
        {
            "id": 58,
            "origem_lote": "proponente",
            "ativacao_id": None,
            "tipo_lead_proponente": "entrada_evento",
            "evento_id": None,
            "plataforma_origem": "drive",
        },
    )()

    lookup_chunk_sizes: list[int] = []

    def _fake_build_payload(row, _batch):
        return dict(row)

    def _fake_find_existing_lead(_db, _payload, anchored_evento_id=None):
        return None

    def _fake_find_existing_from_lookup(_payload, _lookup_context, canonical_evento_id=None):
        return None

    def _fake_load_lookup_context(_db, batch_tuples, canonical_evento_id=None):
        lookup_chunk_sizes.append(len(batch_tuples))
        return lead_pipeline_service.LeadLookupContext([], set(), set())

    monkeypatch.setenv("LEAD_GOLD_INSERT_COMMIT_BATCH_SIZE", "1000")
    monkeypatch.setenv("NPBB_LEAD_GOLD_INSERT_LOOKUP_CHUNK_SIZE", "50")
    monkeypatch.setattr(lead_pipeline_service, "_configure_lead_gold_statement_timeout", lambda _db: None)
    monkeypatch.setattr(lead_pipeline_service, "_build_lead_payload", _fake_build_payload)
    monkeypatch.setattr(lead_pipeline_service, "_find_existing_lead", _fake_find_existing_lead)
    monkeypatch.setattr(lead_pipeline_service, "find_existing_lead_from_lookup", _fake_find_existing_from_lookup)
    monkeypatch.setattr(lead_pipeline_service, "_load_lead_lookup_context", _fake_load_lookup_context)
    monkeypatch.setattr(lead_pipeline_service, "Lead", _FakeLead)

    created = lead_pipeline_service._inserir_leads_gold(fake_batch, csv_path, fake_db)

    assert created == 120
    assert fake_db.flushes == 120
    assert lookup_chunk_sizes == [50, 50, 20]
    assert max(lookup_chunk_sizes) == 50


def test_count_consolidated_csv_data_rows_excludes_header(tmp_path: Path) -> None:
    p = tmp_path / "c.csv"
    with p.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["a", "b"])
        w.writerow([1, 2])
        w.writerow([3, 4])
    assert lead_pipeline_service._count_consolidated_csv_data_rows(p) == 2
