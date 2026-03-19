"""Schemas for FRAMEWORK3 CRUD, orchestration and sync APIs."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.framework_models import (
    AgentMode,
    ArtifactStatus,
    ApprovalStatus,
    AuditGateState,
    DocumentStatus,
    FollowupDestination,
    IssueFormat,
    IntakeKind,
    ProjectStatus,
    ReviewVerdict,
    SourceMode,
    TaskInstructionMode,
)


class FrameworkProjectCreate(BaseModel):
    canonical_name: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    agent_mode: AgentMode = AgentMode.HUMAN_IN_LOOP
    created_by: str = Field(min_length=1, max_length=100)
    owner: str = Field(min_length=1, max_length=100)
    project_root_path: str | None = None
    metadata_json: dict[str, Any] | None = None


class FrameworkProjectUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: ProjectStatus | None = None
    agent_mode: AgentMode | None = None
    owner: str | None = Field(default=None, min_length=1, max_length=100)
    project_root_path: str | None = None
    audit_log_path: str | None = None
    metadata_json: dict[str, Any] | None = None


class FrameworkProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    canonical_name: str
    title: str
    description: str | None = None
    status: ProjectStatus
    agent_mode: AgentMode
    source_of_truth: str
    project_root_path: str | None = None
    audit_log_path: str | None = None
    current_intake_id: int | None = None
    current_prd_id: int | None = None
    created_by: str
    owner: str
    metadata_json: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None


class FrameworkIntakeStructuredPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    problem_statement: str = Field(min_length=1)
    primary_audience: str = Field(min_length=1)
    dominant_job_to_be_done: str = Field(min_length=1)
    main_flow: list[str] = Field(default_factory=list, min_length=1)
    scope_in: list[str] = Field(default_factory=list, min_length=1)
    scope_out: list[str] = Field(default_factory=list, min_length=1)
    business_goal: str = Field(min_length=1)
    success_metrics: list[str] = Field(default_factory=list, min_length=1)
    constraints: list[str] = Field(default_factory=list, min_length=1)
    non_goals: list[str] = Field(default_factory=list, min_length=1)
    dependencies: list[str] = Field(default_factory=list, min_length=1)
    integrations: list[str] = Field(default_factory=list, min_length=1)
    impacted_surfaces: list[str] = Field(default_factory=list, min_length=1)
    risks: list[str] = Field(default_factory=list, min_length=1)


class FrameworkIntakeKnownGap(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(min_length=1)
    description: str = Field(min_length=1)
    blocking: bool
    note: str | None = None


class FrameworkReadinessChecklistItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str = Field(min_length=1)
    label: str = Field(min_length=1)
    completed: bool
    blocking: bool
    note: str | None = None


class FrameworkIntakeVersionEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version_number: int = Field(ge=1)
    created_at: datetime
    summary: str = Field(min_length=1)


class FrameworkIntakeCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    doc_id: str | None = Field(default=None, max_length=200)
    status: ArtifactStatus = ArtifactStatus.DRAFT
    intake_kind: IntakeKind | None = None
    source_mode: SourceMode | None = None
    content_md: str = Field(min_length=1)
    structured_payload: FrameworkIntakeStructuredPayload
    known_gaps: list[FrameworkIntakeKnownGap] = Field(default_factory=list)
    version_history: list[FrameworkIntakeVersionEntry] = Field(default_factory=list)
    readiness_checklist: list[FrameworkReadinessChecklistItem] = Field(default_factory=list)
    ready_for_prd: bool = False
    file_path: str | None = None
    checklist_status_json: dict[str, Any] | None = None
    metadata_json: dict[str, Any] | None = None


class FrameworkIntakeUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    status: ArtifactStatus | None = None
    intake_kind: IntakeKind | None = None
    source_mode: SourceMode | None = None
    content_md: str | None = None
    structured_payload: FrameworkIntakeStructuredPayload | None = None
    known_gaps: list[FrameworkIntakeKnownGap] | None = None
    version_history: list[FrameworkIntakeVersionEntry] | None = None
    readiness_checklist: list[FrameworkReadinessChecklistItem] | None = None
    ready_for_prd: bool | None = None
    file_path: str | None = None
    checklist_status_json: dict[str, Any] | None = None
    metadata_json: dict[str, Any] | None = None


class FrameworkIntakeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    doc_id: str
    title: str
    status: ArtifactStatus
    approval_status: ApprovalStatus
    intake_kind: IntakeKind | None = None
    source_mode: SourceMode | None = None
    content_md: str
    structured_payload: FrameworkIntakeStructuredPayload
    known_gaps: list[FrameworkIntakeKnownGap] = Field(default_factory=list)
    version_history: list[FrameworkIntakeVersionEntry] = Field(default_factory=list)
    readiness_checklist: list[FrameworkReadinessChecklistItem] = Field(default_factory=list)
    ready_for_prd: bool = False
    file_path: str | None = None
    checklist_status_json: dict[str, Any] | None = None
    metadata_json: dict[str, Any] | None = None
    approved_by: str | None = None
    approved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class FrameworkPRDCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    doc_id: str | None = Field(default=None, max_length=200)
    intake_id: int | None = None
    status: ArtifactStatus = ArtifactStatus.DRAFT
    content_md: str = Field(min_length=1)
    file_path: str | None = None
    metadata_json: dict[str, Any] | None = None


class FrameworkPRDUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    intake_id: int | None = None
    status: ArtifactStatus | None = None
    content_md: str | None = None
    file_path: str | None = None
    metadata_json: dict[str, Any] | None = None


class FrameworkPRDRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    intake_id: int | None = None
    doc_id: str
    title: str
    status: ArtifactStatus
    approval_status: ApprovalStatus
    content_md: str
    file_path: str | None = None
    metadata_json: dict[str, Any] | None = None
    approved_by: str | None = None
    approved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class FrameworkPhaseCreate(BaseModel):
    phase_number: int = Field(ge=1)
    name: str = Field(min_length=1, max_length=200)
    slug: str | None = Field(default=None, max_length=120)
    objective: str | None = None
    exit_gate: str | None = None
    scope_in_json: list[str] = Field(default_factory=list)
    scope_out_json: list[str] = Field(default_factory=list)
    dependency_refs_json: list[str] = Field(default_factory=list)
    definition_of_done_json: list[str] = Field(default_factory=list)
    story_points_target: int | None = Field(default=None, ge=0)
    metadata_json: dict[str, Any] | None = None


class FrameworkPhaseUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    slug: str | None = Field(default=None, max_length=120)
    status: DocumentStatus | None = None
    audit_gate: AuditGateState | None = None
    objective: str | None = None
    exit_gate: str | None = None
    scope_in_json: list[str] | None = None
    scope_out_json: list[str] | None = None
    dependency_refs_json: list[str] | None = None
    definition_of_done_json: list[str] | None = None
    story_points_target: int | None = Field(default=None, ge=0)
    file_path: str | None = None
    metadata_json: dict[str, Any] | None = None


class FrameworkPhaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    phase_number: int
    canonical_id: str
    slug: str
    name: str
    status: DocumentStatus
    audit_gate: AuditGateState
    objective: str | None = None
    exit_gate: str | None = None
    scope_in_json: list[str] | None = None
    scope_out_json: list[str] | None = None
    dependency_refs_json: list[str] | None = None
    definition_of_done_json: list[str] | None = None
    story_points_target: int | None = None
    file_path: str | None = None
    metadata_json: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class FrameworkEpicCreate(BaseModel):
    epic_number: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=200)
    slug: str | None = Field(default=None, max_length=120)
    objective: str | None = None
    measurable_outcome: str | None = None
    context_architecture: str | None = None
    dependency_refs_json: list[str] = Field(default_factory=list)
    definition_of_done_json: list[str] = Field(default_factory=list)
    artifact_minimum: str | None = None
    story_points_target: int | None = Field(default=None, ge=0)
    metadata_json: dict[str, Any] | None = None


class FrameworkEpicUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    slug: str | None = Field(default=None, max_length=120)
    status: DocumentStatus | None = None
    objective: str | None = None
    measurable_outcome: str | None = None
    context_architecture: str | None = None
    dependency_refs_json: list[str] | None = None
    definition_of_done_json: list[str] | None = None
    artifact_minimum: str | None = None
    story_points_target: int | None = Field(default=None, ge=0)
    file_path: str | None = None
    metadata_json: dict[str, Any] | None = None


class FrameworkEpicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    phase_id: int
    epic_number: int
    canonical_id: str
    slug: str
    title: str
    objective: str | None = None
    measurable_outcome: str | None = None
    context_architecture: str | None = None
    status: DocumentStatus
    dependency_refs_json: list[str] | None = None
    definition_of_done_json: list[str] | None = None
    artifact_minimum: str | None = None
    story_points_target: int | None = None
    file_path: str | None = None
    metadata_json: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class FrameworkSprintCreate(BaseModel):
    sprint_number: int = Field(ge=1)
    title: str | None = Field(default=None, max_length=200)
    objective: str | None = None
    capacity_story_points: int = Field(default=0, ge=0)
    capacity_issues: int = Field(default=0, ge=0)
    override_note: str | None = None
    risks_text: str | None = None
    closing_decision: str | None = None
    metadata_json: dict[str, Any] | None = None


class FrameworkSprintUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    status: DocumentStatus | None = None
    objective: str | None = None
    capacity_story_points: int | None = Field(default=None, ge=0)
    capacity_issues: int | None = Field(default=None, ge=0)
    override_note: str | None = None
    risks_text: str | None = None
    closing_decision: str | None = None
    file_path: str | None = None
    metadata_json: dict[str, Any] | None = None


class FrameworkSprintRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    phase_id: int
    sprint_number: int
    canonical_id: str
    title: str
    objective: str | None = None
    status: DocumentStatus
    capacity_story_points: int
    capacity_issues: int
    override_note: str | None = None
    risks_text: str | None = None
    closing_decision: str | None = None
    file_path: str | None = None
    metadata_json: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class FrameworkIssueCreate(BaseModel):
    issue_number: int = Field(ge=1)
    sprint_id: int | None = None
    title: str = Field(min_length=1, max_length=220)
    slug: str | None = Field(default=None, max_length=160)
    issue_format: IssueFormat = IssueFormat.DIRECTORY
    task_instruction_mode: TaskInstructionMode = TaskInstructionMode.REQUIRED
    story_points: int = Field(default=1, ge=0, le=5)
    user_story: str | None = None
    technical_context: str | None = None
    tdd_red: str | None = None
    tdd_green: str | None = None
    tdd_refactor: str | None = None
    acceptance_criteria_json: list[str] = Field(default_factory=list)
    definition_of_done_json: list[str] = Field(default_factory=list)
    real_files_json: list[str] = Field(default_factory=list)
    dependency_refs_json: list[str] = Field(default_factory=list)
    decision_refs_json: list[str] = Field(default_factory=list)
    artifact_minimum: str | None = None
    origin_issue_ref: str | None = Field(default=None, max_length=120)
    origin_audit_id: str | None = Field(default=None, max_length=80)
    evidence_ref: str | None = None
    metadata_json: dict[str, Any] | None = None


class FrameworkIssueUpdate(BaseModel):
    sprint_id: int | None = None
    title: str | None = Field(default=None, min_length=1, max_length=220)
    slug: str | None = Field(default=None, max_length=160)
    status: DocumentStatus | None = None
    issue_format: IssueFormat | None = None
    task_instruction_mode: TaskInstructionMode | None = None
    story_points: int | None = Field(default=None, ge=0, le=5)
    user_story: str | None = None
    technical_context: str | None = None
    tdd_red: str | None = None
    tdd_green: str | None = None
    tdd_refactor: str | None = None
    acceptance_criteria_json: list[str] | None = None
    definition_of_done_json: list[str] | None = None
    real_files_json: list[str] | None = None
    dependency_refs_json: list[str] | None = None
    decision_refs_json: list[str] | None = None
    artifact_minimum: str | None = None
    origin_issue_ref: str | None = Field(default=None, max_length=120)
    origin_audit_id: str | None = Field(default=None, max_length=80)
    evidence_ref: str | None = None
    document_path: str | None = None
    metadata_json: dict[str, Any] | None = None


class FrameworkIssueRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    phase_id: int
    epic_id: int
    sprint_id: int | None = None
    issue_number: int
    canonical_id: str
    slug: str
    title: str
    status: DocumentStatus
    issue_format: IssueFormat
    task_instruction_mode: TaskInstructionMode
    story_points: int
    user_story: str | None = None
    technical_context: str | None = None
    tdd_red: str | None = None
    tdd_green: str | None = None
    tdd_refactor: str | None = None
    acceptance_criteria_json: list[str] | None = None
    definition_of_done_json: list[str] | None = None
    real_files_json: list[str] | None = None
    dependency_refs_json: list[str] | None = None
    decision_refs_json: list[str] | None = None
    artifact_minimum: str | None = None
    origin_issue_ref: str | None = None
    origin_audit_id: str | None = None
    evidence_ref: str | None = None
    document_path: str | None = None
    metadata_json: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class FrameworkTaskCreate(BaseModel):
    task_number: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=220)
    objective: str | None = None
    preconditions_json: list[str] = Field(default_factory=list)
    files_to_touch_json: list[str] = Field(default_factory=list)
    tdd_aplicavel: bool = False
    red_tests_json: list[str] = Field(default_factory=list)
    red_command: str | None = None
    red_criteria: str | None = None
    atomic_steps_json: list[str] = Field(default_factory=list)
    allowed_commands_json: list[str] = Field(default_factory=list)
    expected_result: str | None = None
    required_validations_json: list[str] = Field(default_factory=list)
    stop_conditions_json: list[str] = Field(default_factory=list)
    instruction_payload_json: dict[str, Any] | None = None
    metadata_json: dict[str, Any] | None = None


class FrameworkTaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=220)
    status: DocumentStatus | None = None
    objective: str | None = None
    preconditions_json: list[str] | None = None
    files_to_touch_json: list[str] | None = None
    tdd_aplicavel: bool | None = None
    red_tests_json: list[str] | None = None
    red_command: str | None = None
    red_criteria: str | None = None
    atomic_steps_json: list[str] | None = None
    allowed_commands_json: list[str] | None = None
    expected_result: str | None = None
    required_validations_json: list[str] | None = None
    stop_conditions_json: list[str] | None = None
    instruction_payload_json: dict[str, Any] | None = None
    document_path: str | None = None
    executed_by_agent: str | None = None
    executed_at: datetime | None = None
    result_summary: str | None = None
    metadata_json: dict[str, Any] | None = None


class FrameworkTaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    issue_id: int
    task_number: int
    canonical_id: str
    task_id: str
    title: str
    status: DocumentStatus
    objective: str | None = None
    preconditions_json: list[str] | None = None
    files_to_touch_json: list[str] | None = None
    tdd_aplicavel: bool
    red_tests_json: list[str] | None = None
    red_command: str | None = None
    red_criteria: str | None = None
    atomic_steps_json: list[str] | None = None
    allowed_commands_json: list[str] | None = None
    expected_result: str | None = None
    required_validations_json: list[str] | None = None
    stop_conditions_json: list[str] | None = None
    instruction_payload_json: dict[str, Any] | None = None
    document_path: str | None = None
    executed_by_agent: str | None = None
    executed_at: datetime | None = None
    result_summary: str | None = None
    metadata_json: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class FrameworkApprovalRequest(BaseModel):
    actor: str = Field(min_length=1, max_length=100)
    approved: bool
    note: str | None = None
    auto_approved: bool = False


class FrameworkSyncResponse(BaseModel):
    project_id: int
    project_root_path: str
    written_files: list[str]


class FrameworkExecutionPrepareRequest(BaseModel):
    issue_id: int | None = None
    task_selector: str = "auto"
    actor: str = Field(min_length=1, max_length=100)
    agent_model: str = Field(default="manual", min_length=1, max_length=64)


class FrameworkExecutionScopeRead(BaseModel):
    project: FrameworkProjectRead
    phase: FrameworkPhaseRead
    epic: FrameworkEpicRead
    sprint: FrameworkSprintRead | None = None
    issue: FrameworkIssueRead
    task: FrameworkTaskRead
    task_selector: str
    blocked: bool = False
    reason: str | None = None


class FrameworkTaskCompleteRequest(BaseModel):
    actor: str = Field(min_length=1, max_length=100)
    agent_model: str = Field(default="manual", min_length=1, max_length=64)
    result_summary: str | None = None
    evidence_ref: str | None = None
    commit_ref: str | None = None


class FrameworkReviewIssueRequest(BaseModel):
    actor: str = Field(min_length=1, max_length=100)
    base_commit: str = Field(min_length=1)
    target_commit: str = Field(min_length=1)
    evidence_ref: str = Field(min_length=1)
    verdict: ReviewVerdict
    destination: FollowupDestination = FollowupDestination.NONE
    summary: str | None = None
    followup_issue_title: str | None = None
    followup_issue_story_points: int | None = Field(default=None, ge=0, le=5)


class FrameworkReviewIssueResponse(BaseModel):
    review_verdict: ReviewVerdict
    destination: FollowupDestination
    created_issue_id: int | None = None
    created_issue_canonical_id: str | None = None


class FrameworkAuditPhaseRequest(BaseModel):
    actor: str = Field(min_length=1, max_length=100)
    reviewer_model: str = Field(default="manual", min_length=1, max_length=64)
    base_commit: str = Field(min_length=1)
    verdict: str = Field(min_length=1)
    findings_summary: str | None = None
    followup_destination: FollowupDestination = FollowupDestination.NONE
    followup_issue_title: str | None = None
    followup_issue_story_points: int | None = Field(default=None, ge=0, le=5)


class FrameworkAuditPhaseResponse(BaseModel):
    phase_id: int
    gate_state: AuditGateState
    followup_destination: FollowupDestination
    created_issue_id: int | None = None
    created_issue_canonical_id: str | None = None


class FrameworkProjectSnapshot(BaseModel):
    project: FrameworkProjectRead
    current_intake: FrameworkIntakeRead | None = None
    current_prd: FrameworkPRDRead | None = None
    phases: list[FrameworkPhaseRead] = Field(default_factory=list)
    epics: list[FrameworkEpicRead] = Field(default_factory=list)
    sprints: list[FrameworkSprintRead] = Field(default_factory=list)
    issues: list[FrameworkIssueRead] = Field(default_factory=list)
    tasks: list[FrameworkTaskRead] = Field(default_factory=list)
    counts: dict[str, int] = Field(default_factory=dict)
    next_action: str
