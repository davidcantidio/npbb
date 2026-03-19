from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError
from sqlmodel import Session

from app.models.framework_models import ApprovalStatus, FrameworkIntake
from app.schemas.framework import (
    FrameworkIntakeCreate,
    FrameworkIntakeGenerateRequest,
    FrameworkIntakeRead,
    IntakeKind,
    SourceMode,
)
from app.services.framework_orchestrator import AgentOrchestrator
from app.models.framework_models import FrameworkProject


def _structured_payload() -> dict[str, object]:
    return {
        "problem_statement": "O PM ainda depende de montagem manual de artefatos.",
        "primary_audience": "PM",
        "dominant_job_to_be_done": "Abrir um projeto governado no FW5.",
        "main_flow": [
            "Receber contexto bruto",
            "Gerar intake estruturado",
            "Validar prontidao para PRD",
        ],
        "scope_in": [
            "Captura de contexto bruto",
            "Estruturacao do intake",
        ],
        "scope_out": [
            "Geracao do PRD",
        ],
        "business_goal": "Reduzir o trabalho manual de abertura do projeto.",
        "success_metrics": [
            "tempo_manual_reduzido",
        ],
        "constraints": [
            "Manter compatibilidade com a governanca vigente",
        ],
        "non_goals": [
            "Nao substituir toda a governanca markdown nesta task",
        ],
        "dependencies": [
            "GOV-INTAKE.md",
        ],
        "integrations": [
            "framework-governanca",
        ],
        "impacted_surfaces": [
            "backend-api",
            "admin-panel",
        ],
        "risks": [
            "Consolidar hipoteses como fatos",
        ],
    }


def _known_gap() -> dict[str, object]:
    return {
        "code": "gap-ux-opening",
        "description": "A UX final da abertura assistida ainda nao esta fechada.",
        "blocking": True,
        "note": "Nao seguir para PRD enquanto o impacto no fluxo nao estiver claro.",
    }


def _checklist_item() -> dict[str, object]:
    return {
        "key": "problem_statement",
        "label": "Problema ou oportunidade esta claro",
        "completed": True,
        "blocking": True,
        "note": "Origem ja rastreada no intake.",
    }


def _version_entry() -> dict[str, object]:
    return {
        "version_number": 1,
        "created_at": datetime(2026, 3, 19, 12, 0, tzinfo=timezone.utc),
        "summary": "Versao inicial derivada do contexto bruto.",
    }


def _complete_raw_context() -> str:
    return """
Problema ou oportunidade: O PM ainda depende de montagem manual de artefatos.
Publico principal: PM
Job to be done dominante: Abrir um projeto governado no FW5.
Fluxo principal:
- Receber contexto bruto
- Gerar intake estruturado
- Validar prontidao para PRD
Escopo dentro:
- Captura de contexto bruto
- Estruturacao do intake
Escopo fora:
- Geracao do PRD
Objetivo de negocio: Reduzir o trabalho manual de abertura do projeto.
Metricas de sucesso:
- tempo_manual_reduzido
Restricoes:
- Manter compatibilidade com a governanca vigente
Nao objetivos:
- Nao substituir toda a governanca markdown nesta task
Dependencias:
- GOV-INTAKE.md
Integracoes:
- framework-governanca
Superficies impactadas:
- backend-api
- admin-panel
Riscos:
- Consolidar hipoteses como fatos
""".strip()


def _incomplete_raw_context() -> str:
    return """
Problema ou oportunidade: O PM ainda depende de montagem manual de artefatos.
Objetivo de negocio: Reduzir o trabalho manual de abertura do projeto.
Riscos:
- Consolidar hipoteses como fatos
""".strip()


def _create_project(session: Session, canonical_name: str = "fw5-intake-flow") -> FrameworkProject:
    project = FrameworkProject(
        canonical_name=canonical_name,
        title="FW5 Intake Flow",
        created_by="pm",
        owner="pm",
    )
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


def test_framework_intake_schema_requires_structured_payload_fields() -> None:
    with pytest.raises(ValidationError) as exc_info:
        FrameworkIntakeCreate(
            title="FW5 Intake",
            content_md="# Intake",
            structured_payload={
                "primary_audience": "PM",
                "dominant_job_to_be_done": "Abrir projeto",
                "main_flow": ["Receber contexto"],
                "scope_in": ["Intake"],
                "scope_out": ["PRD"],
                "business_goal": "Reduzir trabalho manual",
                "success_metrics": ["tempo_manual_reduzido"],
                "constraints": ["Compatibilidade com governanca"],
                "non_goals": ["Sem PRD nesta task"],
                "dependencies": ["GOV-INTAKE.md"],
                "integrations": ["framework-governanca"],
                "impacted_surfaces": ["backend-api"],
                "risks": ["Escopo ambiguo"],
            },
        )

    assert "problem_statement" in str(exc_info.value)


def test_framework_intake_schema_serializes_gaps_checklist_and_version_history() -> None:
    payload = FrameworkIntakeCreate(
        title="FW5 Intake",
        content_md="# Intake",
        structured_payload=_structured_payload(),
        known_gaps=[_known_gap()],
        readiness_checklist=[_checklist_item()],
        version_history=[_version_entry()],
        ready_for_prd=False,
    )

    assert payload.known_gaps[0].blocking is True
    assert payload.readiness_checklist[0].key == "problem_statement"
    assert payload.version_history[0].version_number == 1
    assert payload.ready_for_prd is False


def test_framework_intake_generation_from_raw_context_persists_structured_payload(db_session: Session) -> None:
    project = _create_project(db_session)
    orchestrator = AgentOrchestrator(db_session)

    intake = orchestrator.process_intake(
        project.id,
        FrameworkIntakeGenerateRequest(
            title="FW5 Intake",
            raw_context=_complete_raw_context(),
            intake_kind=IntakeKind.NEW_CAPABILITY,
            source_mode=SourceMode.ORIGINAL,
        ),
    )

    assert intake.project_id == project.id
    assert intake.doc_id == "INTAKE-FW5-INTAKE-FLOW"
    assert intake.structured_payload["problem_statement"].startswith("O PM")
    assert intake.structured_payload["primary_audience"] == "PM"
    assert intake.ready_for_prd is True
    assert intake.known_gaps == []
    assert intake.readiness_checklist[0]["completed"] is True
    assert intake.version_history[0]["version_number"] == 1


def test_framework_intake_generation_blocks_prd_when_required_fields_are_missing(
    db_session: Session,
) -> None:
    project = _create_project(db_session, canonical_name="fw5-intake-gaps")
    orchestrator = AgentOrchestrator(db_session)

    intake = orchestrator.process_intake(
        project.id,
        FrameworkIntakeGenerateRequest(
            title="FW5 Intake",
            raw_context=_incomplete_raw_context(),
            intake_kind=IntakeKind.NEW_CAPABILITY,
            source_mode=SourceMode.ORIGINAL,
        ),
    )

    assert intake.ready_for_prd is False
    assert any(gap["code"] == "missing-primary_audience" and gap["blocking"] for gap in intake.known_gaps)
    assert any(
        item["key"] == "primary_audience" and item["completed"] is False and item["blocking"] is True
        for item in intake.readiness_checklist
    )
    assert intake.structured_payload["primary_audience"] == "nao_definido"
    assert intake.metadata_json["evidence_map"]["primary_audience"]["classification"] == "hypothesis"


def test_framework_intake_read_round_trips_typed_contract_from_model_helpers() -> None:
    intake = FrameworkIntake(
        project_id=1,
        doc_id="INTAKE-FW5",
        title="FW5 Intake",
        content_md="# Intake",
        approval_status=ApprovalStatus.PENDING,
        checklist_status_json={
            "ready_for_prd": False,
            "items": [_checklist_item()],
        },
        metadata_json={
            "structured_payload": _structured_payload(),
            "known_gaps": [_known_gap()],
            "version_history": [_version_entry()],
        },
    )

    read_model = FrameworkIntakeRead.model_validate(intake)

    assert read_model.structured_payload.problem_statement.startswith("O PM")
    assert read_model.known_gaps[0].blocking is True
    assert read_model.readiness_checklist[0].blocking is True
    assert read_model.version_history[0].version_number == 1
    assert read_model.ready_for_prd is False
    assert read_model.approval_status == ApprovalStatus.PENDING
