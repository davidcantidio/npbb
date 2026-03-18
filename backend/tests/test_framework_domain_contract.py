from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, get_args

import sqlalchemy as sa

from app.models.framework_models import (
    AgentExecution,
    AgentMode,
    ApprovalStatus,
    AuditGateState,
    DocumentStatus,
    FollowupDestination,
    FrameworkIntake,
    FrameworkIssue,
    FrameworkPRD,
    FrameworkPhase,
    FrameworkProject,
    FrameworkTask,
    IssueFormat,
    ProjectStatus,
    ReviewVerdict,
    TaskInstructionMode,
)
from app.schemas.framework import (
    FrameworkIntakeCreate,
    FrameworkIntakeRead,
    FrameworkIntakeUpdate,
    FrameworkPRDCreate,
    FrameworkPRDRead,
    FrameworkPRDUpdate,
)


def _enum_values(enum_cls: type[Enum]) -> tuple[str, ...]:
    return tuple(member.value for member in enum_cls)


def _annotation_enum_values(annotation: Any) -> tuple[str, ...]:
    if isinstance(annotation, type) and issubclass(annotation, Enum):
        return _enum_values(annotation)

    for arg in get_args(annotation):
        if isinstance(arg, type) and issubclass(arg, Enum):
            return _enum_values(arg)

    raise AssertionError(f"expected enum annotation, got {annotation!r}")


def _assert_sqlalchemy_enum(
    table: sa.Table,
    column_name: str,
    expected_values: tuple[str, ...],
) -> None:
    column = table.c[column_name]
    assert isinstance(column.type, sa.Enum)
    assert tuple(column.type.enums) == expected_values


def _table_block(contents: str, table_name: str) -> str:
    marker = f"op.create_table('{table_name}'"
    start = contents.index(marker)
    end = contents.find("op.create_table('", start + len(marker))
    if end == -1:
        return contents[start:]
    return contents[start:end]


def test_framework_enum_domains_match_canonical_contract() -> None:
    assert _enum_values(ProjectStatus) == (
        "draft",
        "intake",
        "prd",
        "planning",
        "execution",
        "audit",
        "completed",
        "cancelled",
    )
    assert _enum_values(DocumentStatus) == ("todo", "active", "done", "cancelled")
    assert _enum_values(ApprovalStatus) == ("pending", "approved", "rejected", "auto_approved")
    assert _enum_values(AgentMode) == ("human_in_loop", "semi_autonomous", "fully_autonomous")
    assert _enum_values(AuditGateState) == ("not_ready", "pending", "hold", "approved")
    assert _enum_values(IssueFormat) == ("directory", "legacy")
    assert _enum_values(TaskInstructionMode) == ("optional", "required")
    assert _enum_values(ReviewVerdict) == ("aprovada", "correcao_requerida", "cancelled")
    assert _enum_values(FollowupDestination) == (
        "none",
        "issue-local",
        "new-intake",
        "cancelled",
    )


def test_framework_models_materialize_canonical_ids_and_controlled_taxonomies() -> None:
    assert {"canonical_name", "status", "agent_mode"} <= set(FrameworkProject.__table__.columns.keys())
    assert {"canonical_id", "audit_gate", "definition_of_done_json"} <= set(
        FrameworkPhase.__table__.columns.keys()
    )
    assert {
        "canonical_id",
        "issue_format",
        "task_instruction_mode",
        "acceptance_criteria_json",
        "definition_of_done_json",
        "origin_audit_id",
        "document_path",
    } <= set(FrameworkIssue.__table__.columns.keys())
    assert {
        "canonical_id",
        "task_id",
        "red_tests_json",
        "red_command",
        "red_criteria",
        "instruction_payload_json",
        "document_path",
    } <= set(FrameworkTask.__table__.columns.keys())
    assert {"target_ref", "human_approval", "evidence_ref"} <= set(
        AgentExecution.__table__.columns.keys()
    )

    _assert_sqlalchemy_enum(
        FrameworkProject.__table__,
        "status",
        ("draft", "intake", "prd", "planning", "execution", "audit", "completed", "cancelled"),
    )
    _assert_sqlalchemy_enum(
        FrameworkProject.__table__,
        "agent_mode",
        ("human_in_loop", "semi_autonomous", "fully_autonomous"),
    )
    _assert_sqlalchemy_enum(
        FrameworkIntake.__table__,
        "status",
        ("draft", "active", "done", "cancelled"),
    )
    _assert_sqlalchemy_enum(
        FrameworkIntake.__table__,
        "intake_kind",
        ("new-product", "new-capability", "problem", "refactor", "audit-remediation"),
    )
    _assert_sqlalchemy_enum(
        FrameworkIntake.__table__,
        "source_mode",
        ("original", "backfilled", "audit-derived"),
    )
    _assert_sqlalchemy_enum(
        FrameworkPRD.__table__,
        "status",
        ("draft", "active", "done", "cancelled"),
    )
    _assert_sqlalchemy_enum(
        FrameworkPhase.__table__,
        "status",
        ("todo", "active", "done", "cancelled"),
    )
    _assert_sqlalchemy_enum(
        FrameworkPhase.__table__,
        "audit_gate",
        ("not_ready", "pending", "hold", "approved"),
    )
    _assert_sqlalchemy_enum(
        FrameworkIssue.__table__,
        "issue_format",
        ("directory", "legacy"),
    )
    _assert_sqlalchemy_enum(
        FrameworkIssue.__table__,
        "task_instruction_mode",
        ("optional", "required"),
    )


def test_framework_schemas_use_controlled_types_for_intake_and_prd_contracts() -> None:
    expected_status = ("draft", "active", "done", "cancelled")
    expected_intake_kind = (
        "new-product",
        "new-capability",
        "problem",
        "refactor",
        "audit-remediation",
    )
    expected_source_mode = ("original", "backfilled", "audit-derived")

    for schema_cls in (
        FrameworkIntakeCreate,
        FrameworkIntakeUpdate,
        FrameworkIntakeRead,
        FrameworkPRDCreate,
        FrameworkPRDUpdate,
        FrameworkPRDRead,
    ):
        assert _annotation_enum_values(schema_cls.model_fields["status"].annotation) == expected_status

    for schema_cls in (FrameworkIntakeCreate, FrameworkIntakeUpdate, FrameworkIntakeRead):
        assert (
            _annotation_enum_values(schema_cls.model_fields["intake_kind"].annotation)
            == expected_intake_kind
        )
        assert (
            _annotation_enum_values(schema_cls.model_fields["source_mode"].annotation)
            == expected_source_mode
        )


def test_framework_initial_revision_reflects_the_canonical_contract() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    revision_path = (
        backend_dir
        / "alembic"
        / "versions"
        / "c0d63429d56d_add_lead_evento_table_for_issue_f1_01_.py"
    )
    contents = revision_path.read_text(encoding="utf-8")

    intake_block = _table_block(contents, "framework_intake")
    assert "sa.Column('doc_id'" in intake_block
    assert "sa.Column('title'" in intake_block
    assert "sa.Column('content_md'" in intake_block
    assert "sa.Column('approval_status'" in intake_block
    assert "sa.Column('intake_kind'" in intake_block
    assert "sa.Column('source_mode'" in intake_block
    assert "sa.Column('validated'" not in intake_block
    assert "sa.Column('content', sa.Text()" not in intake_block

    prd_block = _table_block(contents, "framework_prd")
    assert "sa.Column('doc_id'" in prd_block
    assert "sa.Column('title'" in prd_block
    assert "sa.Column('content_md'" in prd_block
    assert "sa.Column('approval_status'" in prd_block
    assert "sa.Column('approved'" not in prd_block
    assert "sa.Column('content', sa.Text()" not in prd_block

    project_block = _table_block(contents, "framework_project")
    assert "current_intake_id" in project_block
    assert "current_prd_id" in project_block
    assert "framework_project_status" in project_block
    assert "framework_agent_mode" in project_block
    assert "'draft', 'intake', 'prd', 'planning', 'execution', 'audit', 'completed', 'cancelled'" in project_block

    agent_execution_block = _table_block(contents, "agent_execution")
    assert "sa.Column('phase_id'" in agent_execution_block
    assert "sa.Column('issue_id'" in agent_execution_block
    assert "sa.Column('task_id'" in agent_execution_block
    assert "sa.Column('target_ref'" in agent_execution_block
    assert "sa.Column('evidence_ref'" in agent_execution_block
    assert "framework_approval_status" in agent_execution_block

    phase_block = _table_block(contents, "framework_phase")
    assert "sa.Column('canonical_id'" in phase_block
    assert "sa.Column('slug'" in phase_block
    assert "framework_document_status" in phase_block
    assert "framework_audit_gate_state" in phase_block
    assert "'todo', 'active', 'done', 'cancelled'" in phase_block
    assert "'not_ready', 'pending', 'hold', 'approved'" in phase_block
    assert "name='projectstatus'" not in phase_block

    epic_block = _table_block(contents, "framework_epic")
    assert "sa.Column('project_id'" in epic_block
    assert "sa.Column('epic_number'" in epic_block
    assert "sa.Column('canonical_id'" in epic_block
    assert "sa.Column('definition_of_done_json'" in epic_block
    assert "sa.Column('artifact_minimum'" in epic_block
    assert "sa.Column('epic_id', sqlmodel.sql.sqltypes.AutoString()" not in epic_block

    issue_block = _table_block(contents, "framework_issue")
    assert "sa.Column('project_id'" in issue_block
    assert "sa.Column('epic_id'" in issue_block
    assert "sa.Column('sprint_id'" in issue_block
    assert "sa.Column('issue_number'" in issue_block
    assert "sa.Column('canonical_id'" in issue_block
    assert "sa.Column('issue_format'" in issue_block
    assert "sa.Column('task_instruction_mode'" in issue_block
    assert "sa.Column('acceptance_criteria_json'" in issue_block
    assert "sa.Column('definition_of_done_json'" in issue_block
    assert "sa.Column('origin_audit_id'" in issue_block
    assert "sa.Column('document_path'" in issue_block
    assert "sa.Column('issue_id', sqlmodel.sql.sqltypes.AutoString()" not in issue_block
    assert "sa.Column('content', sa.Text()" not in issue_block

    task_block = _table_block(contents, "framework_task")
    assert "sa.Column('project_id'" in task_block
    assert "sa.Column('canonical_id'" in task_block
    assert "sa.Column('task_id'" in task_block
    assert "sa.Column('preconditions_json'" in task_block
    assert "sa.Column('files_to_touch_json'" in task_block
    assert "sa.Column('red_tests_json'" in task_block
    assert "sa.Column('red_command'" in task_block
    assert "sa.Column('red_criteria'" in task_block
    assert "sa.Column('atomic_steps_json'" in task_block
    assert "sa.Column('allowed_commands_json'" in task_block
    assert "sa.Column('required_validations_json'" in task_block
    assert "sa.Column('stop_conditions_json'" in task_block
    assert "sa.Column('instruction_payload_json'" in task_block
    assert "sa.Column('document_path'" in task_block
    assert "sa.Column('instruction', sa.Text()" not in task_block
