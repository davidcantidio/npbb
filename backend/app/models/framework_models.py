from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from sqlalchemy import JSON, Column, DateTime, Enum as SQLEnum, Text, UniqueConstraint
from sqlmodel import Field, Relationship

from app.db.metadata import SQLModel


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class ProjectStatus(str, Enum):
    DRAFT = "draft"
    INTAKE = "intake"
    PRD = "prd"
    PLANNING = "planning"
    EXECUTION = "execution"
    AUDIT = "audit"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DocumentStatus(str, Enum):
    TODO = "todo"
    ACTIVE = "active"
    DONE = "done"
    CANCELLED = "cancelled"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    AUTO_APPROVED = "auto_approved"


class AgentMode(str, Enum):
    HUMAN_IN_LOOP = "human_in_loop"
    SEMI_AUTONOMOUS = "semi_autonomous"
    FULLY_AUTONOMOUS = "fully_autonomous"


class AuditGateState(str, Enum):
    NOT_READY = "not_ready"
    PENDING = "pending"
    HOLD = "hold"
    APPROVED = "approved"


class IssueFormat(str, Enum):
    DIRECTORY = "directory"
    LEGACY = "legacy"


class TaskInstructionMode(str, Enum):
    OPTIONAL = "optional"
    REQUIRED = "required"


class ReviewVerdict(str, Enum):
    APROVADA = "aprovada"
    CORRECAO_REQUERIDA = "correcao_requerida"
    CANCELLED = "cancelled"


class FollowupDestination(str, Enum):
    NONE = "none"
    ISSUE_LOCAL = "issue-local"
    NEW_INTAKE = "new-intake"
    CANCELLED = "cancelled"


class FrameworkProject(SQLModel, table=True):
    """Top-level FRAMEWORK3 project."""

    __tablename__ = "framework_project"

    id: Optional[int] = Field(default=None, primary_key=True)
    canonical_name: str = Field(max_length=100, unique=True, index=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    status: ProjectStatus = Field(
        default=ProjectStatus.DRAFT,
        sa_column=Column(SQLEnum(ProjectStatus, name="framework_project_status"), nullable=False),
    )
    agent_mode: AgentMode = Field(
        default=AgentMode.HUMAN_IN_LOOP,
        sa_column=Column(SQLEnum(AgentMode, name="framework_agent_mode"), nullable=False),
    )
    source_of_truth: str = Field(default="markdown_primary", max_length=40)
    project_root_path: Optional[str] = Field(default=None, max_length=500)
    audit_log_path: Optional[str] = Field(default=None, max_length=500)
    current_intake_id: Optional[int] = Field(default=None, index=True)
    current_prd_id: Optional[int] = Field(default=None, index=True)
    created_by: str = Field(max_length=100)
    owner: str = Field(max_length=100)
    metadata_json: Optional[dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc),
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    intakes: list["FrameworkIntake"] = Relationship(back_populates="project")
    prds: list["FrameworkPRD"] = Relationship(back_populates="project")
    phases: list["FrameworkPhase"] = Relationship(back_populates="project")
    sprints: list["FrameworkSprint"] = Relationship(back_populates="project")
    issues: list["FrameworkIssue"] = Relationship(back_populates="project")
    tasks: list["FrameworkTask"] = Relationship(back_populates="project")
    agent_executions: list["AgentExecution"] = Relationship(back_populates="project")


class FrameworkIntake(SQLModel, table=True):
    """Persisted intake document state."""

    __tablename__ = "framework_intake"
    __table_args__ = (UniqueConstraint("project_id", "doc_id", name="uq_framework_intake_doc"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="framework_project.id", index=True)
    doc_id: str = Field(max_length=200)
    title: str = Field(max_length=200)
    status: str = Field(default="draft", max_length=32, index=True)
    approval_status: ApprovalStatus = Field(
        default=ApprovalStatus.PENDING,
        sa_column=Column(SQLEnum(ApprovalStatus, name="framework_approval_status"), nullable=False),
    )
    intake_kind: Optional[str] = Field(default=None, max_length=64)
    source_mode: Optional[str] = Field(default=None, max_length=64)
    content_md: str = Field(sa_column=Column(Text, nullable=False))
    file_path: Optional[str] = Field(default=None, max_length=500)
    checklist_status_json: Optional[dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    metadata_json: Optional[dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    approved_by: Optional[str] = Field(default=None, max_length=100)
    approved_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc),
    )

    project: Optional[FrameworkProject] = Relationship(back_populates="intakes")


class FrameworkPRD(SQLModel, table=True):
    """Persisted PRD document state."""

    __tablename__ = "framework_prd"
    __table_args__ = (UniqueConstraint("project_id", "doc_id", name="uq_framework_prd_doc"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="framework_project.id", index=True)
    intake_id: Optional[int] = Field(default=None, foreign_key="framework_intake.id", index=True)
    doc_id: str = Field(max_length=200)
    title: str = Field(max_length=200)
    status: str = Field(default="draft", max_length=32, index=True)
    approval_status: ApprovalStatus = Field(
        default=ApprovalStatus.PENDING,
        sa_column=Column(SQLEnum(ApprovalStatus, name="framework_approval_status"), nullable=False),
    )
    content_md: str = Field(sa_column=Column(Text, nullable=False))
    file_path: Optional[str] = Field(default=None, max_length=500)
    metadata_json: Optional[dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    approved_by: Optional[str] = Field(default=None, max_length=100)
    approved_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc),
    )

    project: Optional[FrameworkProject] = Relationship(back_populates="prds")


class FrameworkPhase(SQLModel, table=True):
    """Project phase manifest and gate state."""

    __tablename__ = "framework_phase"
    __table_args__ = (
        UniqueConstraint("project_id", "phase_number", name="uq_framework_phase_number"),
        UniqueConstraint("project_id", "canonical_id", name="uq_framework_phase_canonical"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="framework_project.id", index=True)
    phase_number: int = Field(index=True)
    canonical_id: str = Field(max_length=32, index=True)
    slug: str = Field(max_length=120)
    name: str = Field(max_length=200)
    status: DocumentStatus = Field(
        default=DocumentStatus.TODO,
        sa_column=Column(SQLEnum(DocumentStatus, name="framework_document_status"), nullable=False),
    )
    audit_gate: AuditGateState = Field(
        default=AuditGateState.NOT_READY,
        sa_column=Column(SQLEnum(AuditGateState, name="framework_audit_gate_state"), nullable=False),
    )
    objective: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    exit_gate: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    scope_in_json: Optional[list[str]] = Field(default=None, sa_column=Column(JSON, nullable=True))
    scope_out_json: Optional[list[str]] = Field(default=None, sa_column=Column(JSON, nullable=True))
    dependency_refs_json: Optional[list[str]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    definition_of_done_json: Optional[list[str]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    story_points_target: Optional[int] = Field(default=None)
    file_path: Optional[str] = Field(default=None, max_length=500)
    metadata_json: Optional[dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc),
    )

    project: Optional[FrameworkProject] = Relationship(back_populates="phases")
    epics: list["FrameworkEpic"] = Relationship(back_populates="phase")
    sprints: list["FrameworkSprint"] = Relationship(back_populates="phase")
    issues: list["FrameworkIssue"] = Relationship(back_populates="phase")


class FrameworkEpic(SQLModel, table=True):
    """Phase epic manifest."""

    __tablename__ = "framework_epic"
    __table_args__ = (
        UniqueConstraint("phase_id", "epic_number", name="uq_framework_epic_number"),
        UniqueConstraint("project_id", "canonical_id", name="uq_framework_epic_canonical"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="framework_project.id", index=True)
    phase_id: int = Field(foreign_key="framework_phase.id", index=True)
    epic_number: int = Field(index=True)
    canonical_id: str = Field(max_length=32, index=True)
    slug: str = Field(max_length=120)
    title: str = Field(max_length=200)
    objective: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    measurable_outcome: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    context_architecture: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    status: DocumentStatus = Field(
        default=DocumentStatus.TODO,
        sa_column=Column(SQLEnum(DocumentStatus, name="framework_document_status"), nullable=False),
    )
    dependency_refs_json: Optional[list[str]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    definition_of_done_json: Optional[list[str]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    artifact_minimum: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    story_points_target: Optional[int] = Field(default=None)
    file_path: Optional[str] = Field(default=None, max_length=500)
    metadata_json: Optional[dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc),
    )

    project: Optional[FrameworkProject] = Relationship()
    phase: Optional[FrameworkPhase] = Relationship(back_populates="epics")
    issues: list["FrameworkIssue"] = Relationship(back_populates="epic")


class FrameworkSprint(SQLModel, table=True):
    """Sprint manifesto used for operational selection."""

    __tablename__ = "framework_sprint"
    __table_args__ = (
        UniqueConstraint("phase_id", "sprint_number", name="uq_framework_sprint_number"),
        UniqueConstraint("project_id", "canonical_id", name="uq_framework_sprint_canonical"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="framework_project.id", index=True)
    phase_id: int = Field(foreign_key="framework_phase.id", index=True)
    sprint_number: int = Field(index=True)
    canonical_id: str = Field(max_length=32, index=True)
    title: str = Field(max_length=200)
    objective: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    status: DocumentStatus = Field(
        default=DocumentStatus.TODO,
        sa_column=Column(SQLEnum(DocumentStatus, name="framework_document_status"), nullable=False),
    )
    capacity_story_points: int = Field(default=0)
    capacity_issues: int = Field(default=0)
    override_note: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    risks_text: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    closing_decision: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    file_path: Optional[str] = Field(default=None, max_length=500)
    metadata_json: Optional[dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc),
    )

    project: Optional[FrameworkProject] = Relationship(back_populates="sprints")
    phase: Optional[FrameworkPhase] = Relationship(back_populates="sprints")
    issues: list["FrameworkIssue"] = Relationship(back_populates="sprint")


class FrameworkIssue(SQLModel, table=True):
    """Issue manifest, in directory or legacy form."""

    __tablename__ = "framework_issue"
    __table_args__ = (
        UniqueConstraint("epic_id", "issue_number", name="uq_framework_issue_number"),
        UniqueConstraint("project_id", "canonical_id", name="uq_framework_issue_canonical"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="framework_project.id", index=True)
    phase_id: int = Field(foreign_key="framework_phase.id", index=True)
    epic_id: int = Field(foreign_key="framework_epic.id", index=True)
    sprint_id: Optional[int] = Field(default=None, foreign_key="framework_sprint.id", index=True)
    issue_number: int = Field(index=True)
    canonical_id: str = Field(max_length=48, index=True)
    slug: str = Field(max_length=160)
    title: str = Field(max_length=220)
    status: DocumentStatus = Field(
        default=DocumentStatus.TODO,
        sa_column=Column(SQLEnum(DocumentStatus, name="framework_document_status"), nullable=False),
    )
    issue_format: IssueFormat = Field(
        default=IssueFormat.DIRECTORY,
        sa_column=Column(SQLEnum(IssueFormat, name="framework_issue_format"), nullable=False),
    )
    task_instruction_mode: TaskInstructionMode = Field(
        default=TaskInstructionMode.REQUIRED,
        sa_column=Column(
            SQLEnum(TaskInstructionMode, name="framework_task_instruction_mode"),
            nullable=False,
        ),
    )
    story_points: int = Field(default=1)
    user_story: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    technical_context: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    tdd_red: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    tdd_green: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    tdd_refactor: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    acceptance_criteria_json: Optional[list[str]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    definition_of_done_json: Optional[list[str]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    real_files_json: Optional[list[str]] = Field(default=None, sa_column=Column(JSON, nullable=True))
    dependency_refs_json: Optional[list[str]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    decision_refs_json: Optional[list[str]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    artifact_minimum: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    origin_issue_ref: Optional[str] = Field(default=None, max_length=120)
    origin_audit_id: Optional[str] = Field(default=None, max_length=80)
    evidence_ref: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    document_path: Optional[str] = Field(default=None, max_length=500)
    metadata_json: Optional[dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc),
    )

    project: Optional[FrameworkProject] = Relationship(back_populates="issues")
    phase: Optional[FrameworkPhase] = Relationship(back_populates="issues")
    epic: Optional[FrameworkEpic] = Relationship(back_populates="issues")
    sprint: Optional[FrameworkSprint] = Relationship(back_populates="issues")
    tasks: list["FrameworkTask"] = Relationship(back_populates="issue")


class FrameworkTask(SQLModel, table=True):
    """Task file or inline instruction payload materialized in the database."""

    __tablename__ = "framework_task"
    __table_args__ = (
        UniqueConstraint("issue_id", "task_number", name="uq_framework_task_number"),
        UniqueConstraint("project_id", "canonical_id", name="uq_framework_task_canonical"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="framework_project.id", index=True)
    issue_id: int = Field(foreign_key="framework_issue.id", index=True)
    task_number: int = Field(index=True)
    canonical_id: str = Field(max_length=80, index=True)
    task_id: str = Field(max_length=16)
    title: str = Field(max_length=220)
    status: DocumentStatus = Field(
        default=DocumentStatus.TODO,
        sa_column=Column(SQLEnum(DocumentStatus, name="framework_document_status"), nullable=False),
    )
    objective: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    preconditions_json: Optional[list[str]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    files_to_touch_json: Optional[list[str]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    tdd_aplicavel: bool = Field(default=False)
    red_tests_json: Optional[list[str]] = Field(default=None, sa_column=Column(JSON, nullable=True))
    red_command: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    red_criteria: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    atomic_steps_json: Optional[list[str]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    allowed_commands_json: Optional[list[str]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    expected_result: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    required_validations_json: Optional[list[str]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    stop_conditions_json: Optional[list[str]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    instruction_payload_json: Optional[dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    document_path: Optional[str] = Field(default=None, max_length=500)
    executed_by_agent: Optional[str] = Field(default=None, max_length=100)
    executed_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    result_summary: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    metadata_json: Optional[dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc),
    )

    project: Optional[FrameworkProject] = Relationship(back_populates="tasks")
    issue: Optional[FrameworkIssue] = Relationship(back_populates="tasks")


class AgentExecution(SQLModel, table=True):
    """Auditable execution log for planning, execution, review and audit flows."""

    __tablename__ = "agent_execution"

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="framework_project.id", index=True)
    phase_id: Optional[int] = Field(default=None, foreign_key="framework_phase.id", index=True)
    issue_id: Optional[int] = Field(default=None, foreign_key="framework_issue.id", index=True)
    task_id: Optional[int] = Field(default=None, foreign_key="framework_task.id", index=True)
    step: str = Field(max_length=64, index=True)
    target_ref: Optional[str] = Field(default=None, max_length=160)
    prompt_used: str = Field(sa_column=Column(Text, nullable=False))
    output_generated: str = Field(sa_column=Column(Text, nullable=False))
    evidence_ref: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    agent_model: str = Field(default="unknown", max_length=64)
    tokens_used: Optional[int] = Field(default=None)
    duration_ms: Optional[int] = Field(default=None)
    success: bool = Field(default=True)
    human_approval: Optional[ApprovalStatus] = Field(
        default=None,
        sa_column=Column(
            SQLEnum(ApprovalStatus, name="framework_approval_status"),
            nullable=True,
        ),
    )
    approved_by: Optional[str] = Field(default=None, max_length=100)
    metadata_json: Optional[dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    created_at: datetime = Field(default_factory=now_utc)

    project: Optional[FrameworkProject] = Relationship(back_populates="agent_executions")
