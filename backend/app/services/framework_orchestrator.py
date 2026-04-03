from __future__ import annotations

import re
import unicodedata
from datetime import datetime
from typing import Any, Dict, List

from sqlmodel import Session, select

from app.models.framework_models import (
    AgentExecution,
    AgentMode,
    ApprovalStatus,
    ArtifactStatus,
    FrameworkIntake,
    FrameworkPRD,
    FrameworkPhase,
    FrameworkProject,
    IntakeKind,
    ProjectStatus,
    SourceMode,
)
from app.schemas.framework import FrameworkIntakeGenerateRequest


def _normalize_header(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    compact = re.sub(r"[_\-]+", " ", ascii_only.lower())
    return re.sub(r"\s+", " ", compact).strip()


def _strip_list_marker(value: str) -> str:
    return re.sub(r"^(?:[-*]\s+|\d+[.)]\s+)", "", value).strip()


def _split_inline_items(value: str) -> list[str]:
    text = value.strip()
    if not text:
        return []
    if ";" in text:
        parts = text.split(";")
    elif "," in text:
        parts = text.split(",")
    else:
        parts = [text]
    return [part.strip() for part in parts if part.strip()]


_FIELD_SPECS: list[dict[str, Any]] = [
    {
        "key": "problem_statement",
        "label": "Problema ou oportunidade",
        "checklist_label": "Problema ou oportunidade esta claro",
        "is_list": False,
        "aliases": (
            "problema ou oportunidade",
            "problema",
            "problem statement",
        ),
    },
    {
        "key": "primary_audience",
        "label": "Publico principal",
        "checklist_label": "Publico principal esta claro",
        "is_list": False,
        "aliases": (
            "publico principal",
            "publico",
            "publico ou operador principal",
            "primary audience",
        ),
    },
    {
        "key": "dominant_job_to_be_done",
        "label": "Job to be done dominante",
        "checklist_label": "Job to be done dominante esta claro",
        "is_list": False,
        "aliases": (
            "job to be done dominante",
            "job dominante",
            "job to be done",
            "dominant job to be done",
        ),
    },
    {
        "key": "main_flow",
        "label": "Fluxo principal",
        "checklist_label": "Fluxo principal esta descrito",
        "is_list": True,
        "aliases": (
            "fluxo principal",
            "fluxo principal desejado",
            "main flow",
        ),
    },
    {
        "key": "scope_in",
        "label": "Escopo dentro",
        "checklist_label": "Escopo dentro esta declarado",
        "is_list": True,
        "aliases": (
            "escopo dentro",
            "scope in",
            "dentro",
        ),
    },
    {
        "key": "scope_out",
        "label": "Escopo fora",
        "checklist_label": "Escopo fora esta declarado",
        "is_list": True,
        "aliases": (
            "escopo fora",
            "scope out",
            "fora",
        ),
    },
    {
        "key": "business_goal",
        "label": "Objetivo de negocio",
        "checklist_label": "Objetivo de negocio esta declarado",
        "is_list": False,
        "aliases": (
            "objetivo de negocio",
            "business goal",
            "resultado de negocio",
        ),
    },
    {
        "key": "success_metrics",
        "label": "Metricas de sucesso",
        "checklist_label": "Metricas de sucesso estao declaradas",
        "is_list": True,
        "aliases": (
            "metricas de sucesso",
            "success metrics",
            "metricas",
        ),
    },
    {
        "key": "constraints",
        "label": "Restricoes",
        "checklist_label": "Restricoes estao declaradas",
        "is_list": True,
        "aliases": (
            "restricoes",
            "constraints",
            "guardrails",
        ),
    },
    {
        "key": "non_goals",
        "label": "Nao objetivos",
        "checklist_label": "Nao objetivos estao declarados",
        "is_list": True,
        "aliases": (
            "nao objetivos",
            "non goals",
            "nao objetivos",
        ),
    },
    {
        "key": "dependencies",
        "label": "Dependencias",
        "checklist_label": "Dependencias estao declaradas",
        "is_list": True,
        "aliases": (
            "dependencias",
            "dependencies",
        ),
    },
    {
        "key": "integrations",
        "label": "Integracoes",
        "checklist_label": "Integracoes estao declaradas",
        "is_list": True,
        "aliases": (
            "integracoes",
            "integrations",
        ),
    },
    {
        "key": "impacted_surfaces",
        "label": "Superficies impactadas",
        "checklist_label": "Superficies impactadas estao mapeadas",
        "is_list": True,
        "aliases": (
            "superficies impactadas",
            "surfaces impacted",
            "impacted surfaces",
            "arquitetura afetada",
        ),
    },
    {
        "key": "risks",
        "label": "Riscos",
        "checklist_label": "Riscos estao declarados",
        "is_list": True,
        "aliases": (
            "riscos",
            "risks",
        ),
    },
]

_FIELD_BY_ALIAS = {
    _normalize_header(alias): field
    for field in _FIELD_SPECS
    for alias in field["aliases"]
}


class AgentOrchestrator:
    """
    Orquestrador central do FRAMEWORK3.
    Responsavel por gerenciar o fluxo completo:
    Intake -> PRD -> Fases -> Epicos -> Issues -> Tasks -> Auditoria
    com suporte a diferentes modos de operacao.
    """

    def __init__(self, db: Session):
        self.db = db
        self.current_mode = AgentMode.HUMAN_IN_LOOP

    def create_project(self, project_data: Dict[str, Any]) -> FrameworkProject:
        """Cria um novo projeto a partir de um intake inicial."""
        project = FrameworkProject(
            canonical_name=project_data["canonical_name"],
            title=project_data["title"],
            description=project_data.get("description"),
            status=ProjectStatus.DRAFT,
            agent_mode=project_data.get("agent_mode", AgentMode.HUMAN_IN_LOOP),
            created_by=project_data["created_by"],
            owner=project_data.get("owner", project_data["created_by"]),
            project_root_path=project_data.get("project_root_path"),
            metadata_json=project_data.get("metadata_json", project_data.get("metadata", {})),
        )

        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)

        self._log_execution(
            project.id,
            "project_creation",
            f"Projeto {project.canonical_name} criado",
            success=True,
        )

        return project

    def process_intake(
        self,
        project_id: int,
        intake_input: FrameworkIntakeGenerateRequest | dict[str, Any],
    ) -> FrameworkIntake:
        """Gera, valida e persiste um intake estruturado a partir de contexto bruto."""
        project = self.db.get(FrameworkProject, project_id)
        if not project:
            raise LookupError(f"Projeto {project_id} nao encontrado")

        request = (
            intake_input
            if isinstance(intake_input, FrameworkIntakeGenerateRequest)
            else FrameworkIntakeGenerateRequest.model_validate(intake_input)
        )
        doc_id = request.doc_id or f"INTAKE-{project.canonical_name.upper()}"

        structured_payload, evidence_map, known_gaps, readiness_checklist = self._generate_intake_payload(
            request.raw_context
        )
        ready_for_prd = not any(gap["blocking"] for gap in known_gaps) and all(
            item["completed"] or not item["blocking"] for item in readiness_checklist
        )
        version_history = self._initial_version_history()

        evidence_map["ready_for_prd"] = {
            "classification": "inference",
            "derived_from": ["known_gaps", "readiness_checklist"],
            "rule": "true apenas quando nao houver lacuna bloqueante e todo item bloqueante estiver completo",
        }
        evidence_map["version_history"] = {
            "classification": "inference",
            "derived_from": ["raw_context"],
            "rule": "versao inicial criada na primeira geracao do intake",
        }

        checklist_status_json = {
            "ready_for_prd": ready_for_prd,
            "items": readiness_checklist,
        }
        metadata_json = {
            **(request.metadata_json or {}),
            "raw_context": request.raw_context,
            "structured_payload": structured_payload,
            "known_gaps": known_gaps,
            "version_history": version_history,
            "evidence_map": evidence_map,
            "input_taxonomies": {
                "intake_kind": request.intake_kind.value if request.intake_kind else None,
                "source_mode": request.source_mode.value if request.source_mode else None,
            },
            "generation_summary": self._build_generation_summary(structured_payload, known_gaps),
        }
        content_md = self._render_intake_markdown(request.title, structured_payload, known_gaps, readiness_checklist)

        intake = self.db.exec(
            select(FrameworkIntake).where(
                FrameworkIntake.project_id == project_id,
                FrameworkIntake.doc_id == doc_id,
            )
        ).first()
        if intake is None:
            intake = FrameworkIntake(
                project_id=project_id,
                doc_id=doc_id,
                title=request.title,
                status=ArtifactStatus.ACTIVE,
                approval_status=ApprovalStatus.PENDING,
                intake_kind=request.intake_kind or IntakeKind.NEW_CAPABILITY,
                source_mode=request.source_mode or SourceMode.ORIGINAL,
                content_md=content_md,
                file_path=request.file_path,
                checklist_status_json=checklist_status_json,
                metadata_json=metadata_json,
            )
            self.db.add(intake)
        else:
            intake.title = request.title
            intake.status = ArtifactStatus.ACTIVE
            intake.approval_status = ApprovalStatus.PENDING
            intake.intake_kind = request.intake_kind or intake.intake_kind or IntakeKind.NEW_CAPABILITY
            intake.source_mode = request.source_mode or intake.source_mode or SourceMode.ORIGINAL
            intake.content_md = content_md
            intake.file_path = request.file_path
            intake.checklist_status_json = checklist_status_json
            metadata_json["version_history"] = self._next_version_history(intake.version_history)
            intake.metadata_json = metadata_json
            intake.approved_by = None
            intake.approved_at = None

        self.db.commit()
        self.db.refresh(intake)

        project.current_intake_id = intake.id
        project.status = ProjectStatus.INTAKE
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)

        self._log_execution(
            project_id,
            "intake_processing",
            metadata_json["generation_summary"],
            success=True,
        )

        return intake

    def generate_prd(self, intake_id: int, auto_approve: bool = False) -> FrameworkPRD:
        """Gera PRD a partir do intake."""
        intake = self.db.get(FrameworkIntake, intake_id)
        if not intake:
            raise LookupError("Intake nao encontrado")

        prd_content = (
            f"# PRD gerado automaticamente a partir de {intake.doc_id}\n\n"
            "[Conteudo gerado por LLM baseado no intake]"
        )

        prd = FrameworkPRD(
            project_id=intake.project_id,
            intake_id=intake_id,
            doc_id=f"PRD-{intake.doc_id.removeprefix('INTAKE-')}",
            title=f"PRD - {intake.title}",
            content_md=prd_content,
            status=ArtifactStatus.DRAFT,
            approval_status=ApprovalStatus.AUTO_APPROVED if auto_approve else ApprovalStatus.PENDING,
            approved_at=datetime.now() if auto_approve else None,
            approved_by="system" if auto_approve else None,
        )

        self.db.add(prd)
        self.db.commit()
        self.db.refresh(prd)

        project = self.db.get(FrameworkProject, intake.project_id)
        if project:
            project.current_prd_id = prd.id
            self.db.add(project)
            self.db.commit()

        self._log_execution(
            intake.project_id,
            "prd_generation",
            "PRD gerado automaticamente",
            success=True,
        )

        return prd

    def start_planning_pipeline(self, project_id: int) -> List[FrameworkPhase]:
        """Inicia o pipeline de planejamento (fases, epicos, issues)."""
        project = self.db.get(FrameworkProject, project_id)
        if not project:
            raise LookupError(f"Projeto {project_id} nao encontrado")

        phases: list[FrameworkPhase] = []
        phase = FrameworkPhase(
            project_id=project_id,
            phase_number=1,
            canonical_id="F1",
            slug="fundacao-e-estrutura",
            name="Fundacao e Estrutura",
            objective="Estabelecer base do modulo FRAMEWORK3",
        )
        self.db.add(phase)
        self.db.commit()
        self.db.refresh(phase)
        phases.append(phase)

        self._log_execution(
            project_id,
            "planning_pipeline",
            f"Iniciado pipeline de planejamento com {len(phases)} fases",
            success=True,
        )

        return phases

    def execute_next_task(self, project_id: int) -> Dict[str, Any]:
        """Executa a proxima task elegivel (placeholder)."""
        execution = {
            "project_id": project_id,
            "step": "task_execution",
            "status": "started",
            "message": "Buscando proxima task elegivel conforme governanca...",
        }
        self._log_execution(project_id, "task_execution", execution["message"])
        return execution

    def get_project_status(self, project_id: int) -> Dict[str, Any]:
        """Retorna status completo do projeto para UI e orquestracao."""
        project = self.db.get(FrameworkProject, project_id)
        if not project:
            return {"error": "Projeto nao encontrado"}

        return {
            "id": project.id,
            "name": project.canonical_name,
            "status": project.status.value,
            "agent_mode": project.agent_mode.value,
            "has_intake": bool(project.current_intake_id),
            "has_prd": bool(project.current_prd_id),
            "progress": "45%",
            "next_action": self._determine_next_action(project),
        }

    def _determine_next_action(self, project: FrameworkProject) -> str:
        if project.status == ProjectStatus.INTAKE:
            return "Revisar intake"
        if project.status == ProjectStatus.PRD:
            return "Iniciar planejamento de fases"
        if project.status == ProjectStatus.PLANNING:
            return "Gerar issues e tasks"
        if project.status == ProjectStatus.EXECUTION:
            return "Executar proxima task"
        return "Auditoria ou finalizacao"

    def _generate_intake_payload(
        self,
        raw_context: str,
    ) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
        parsed_values, explicit_sources = self._parse_raw_context(raw_context)
        structured_payload: dict[str, Any] = {}
        evidence_map: dict[str, Any] = {}
        known_gaps: list[dict[str, Any]] = []
        readiness_checklist: list[dict[str, Any]] = []

        for field in _FIELD_SPECS:
            key = field["key"]
            explicit_value = parsed_values.get(key)
            source = explicit_sources.get(key, {})
            if field["is_list"]:
                items = list(explicit_value or [])
                cleaned_items = [_strip_list_marker(item) for item in items if _strip_list_marker(item)]
                if cleaned_items:
                    structured_payload[key] = cleaned_items
                    readiness_checklist.append(
                        {
                            "key": key,
                            "label": field["checklist_label"],
                            "completed": True,
                            "blocking": True,
                            "note": "Preenchido a partir do contexto bruto.",
                        }
                    )
                    evidence_map[key] = {
                        "classification": "fact",
                        "source": "raw_context",
                        "matched_alias": source.get("matched_alias"),
                        "source_line": source.get("source_line"),
                    }
                else:
                    structured_payload[key] = ["nao_definido"]
                    readiness_checklist.append(
                        {
                            "key": key,
                            "label": field["checklist_label"],
                            "completed": False,
                            "blocking": True,
                            "note": "Campo ausente; registrado como hipotese controlada.",
                        }
                    )
                    known_gaps.append(self._build_known_gap(key, field["label"]))
                    evidence_map[key] = {
                        "classification": "hypothesis",
                        "source": "placeholder",
                        "reason": "campo obrigatorio ausente no contexto bruto",
                    }
            else:
                text_value = str(explicit_value or "").strip()
                if text_value:
                    structured_payload[key] = text_value
                    readiness_checklist.append(
                        {
                            "key": key,
                            "label": field["checklist_label"],
                            "completed": True,
                            "blocking": True,
                            "note": "Preenchido a partir do contexto bruto.",
                        }
                    )
                    evidence_map[key] = {
                        "classification": "fact",
                        "source": "raw_context",
                        "matched_alias": source.get("matched_alias"),
                        "source_line": source.get("source_line"),
                    }
                else:
                    structured_payload[key] = "nao_definido"
                    readiness_checklist.append(
                        {
                            "key": key,
                            "label": field["checklist_label"],
                            "completed": False,
                            "blocking": True,
                            "note": "Campo ausente; registrado como hipotese controlada.",
                        }
                    )
                    known_gaps.append(self._build_known_gap(key, field["label"]))
                    evidence_map[key] = {
                        "classification": "hypothesis",
                        "source": "placeholder",
                        "reason": "campo obrigatorio ausente no contexto bruto",
                    }

        return structured_payload, evidence_map, known_gaps, readiness_checklist

    def _parse_raw_context(
        self,
        raw_context: str,
    ) -> tuple[dict[str, Any], dict[str, dict[str, str]]]:
        parsed: dict[str, Any] = {}
        sources: dict[str, dict[str, str]] = {}
        current_field: dict[str, Any] | None = None

        for raw_line in raw_context.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            header, separator, remainder = line.partition(":")
            normalized_header = _normalize_header(header)
            candidate = _FIELD_BY_ALIAS.get(normalized_header) if separator else None
            if candidate:
                current_field = candidate
                key = candidate["key"]
                sources[key] = {
                    "matched_alias": header.strip(),
                    "source_line": raw_line.strip(),
                }
                if candidate["is_list"]:
                    inline_items = _split_inline_items(remainder)
                    if inline_items:
                        parsed.setdefault(key, []).extend(inline_items)
                    else:
                        parsed.setdefault(key, [])
                else:
                    parsed[key] = remainder.strip()
                continue

            if current_field is None:
                continue

            key = current_field["key"]
            if current_field["is_list"]:
                parsed.setdefault(key, []).append(line)
            else:
                parsed[key] = " ".join(part for part in [str(parsed.get(key, "")).strip(), line] if part).strip()

        return parsed, sources

    def _build_known_gap(self, key: str, label: str) -> dict[str, Any]:
        return {
            "code": f"missing-{key}",
            "description": f"Campo obrigatorio ausente: {label}.",
            "blocking": True,
            "note": "Preencher antes de seguir para PRD.",
        }

    def _initial_version_history(self) -> list[dict[str, Any]]:
        return [
            {
                "version_number": 1,
                "created_at": datetime.now().astimezone().isoformat(),
                "summary": "Versao inicial derivada do contexto bruto.",
            }
        ]

    def _next_version_history(self, existing_history: list[dict[str, Any]]) -> list[dict[str, Any]]:
        history = list(existing_history or [])
        version_number = max((entry.get("version_number", 0) for entry in history), default=0) + 1
        history.append(
            {
                "version_number": version_number,
                "created_at": datetime.now().astimezone().isoformat(),
                "summary": "Versao atualizada a partir de novo contexto bruto.",
            }
        )
        return history

    def _build_generation_summary(
        self,
        structured_payload: dict[str, Any],
        known_gaps: list[dict[str, Any]],
    ) -> str:
        factual_fields = sum(1 for value in structured_payload.values() if value != "nao_definido" and value != ["nao_definido"])
        return (
            "Intake estruturado a partir de contexto bruto com "
            f"{factual_fields} campos preenchidos e {len(known_gaps)} lacunas bloqueantes."
        )

    def _render_intake_markdown(
        self,
        title: str,
        structured_payload: dict[str, Any],
        known_gaps: list[dict[str, Any]],
        readiness_checklist: list[dict[str, Any]],
    ) -> str:
        sections = [f"# {title}", "", "## Intake Estruturado"]
        for field in _FIELD_SPECS:
            value = structured_payload[field["key"]]
            sections.append(f"### {field['label']}")
            if field["is_list"]:
                sections.extend(f"- {item}" for item in value)
            else:
                sections.append(value)
            sections.append("")

        sections.extend(["## Lacunas Conhecidas"])
        if known_gaps:
            for gap in known_gaps:
                sections.append(f"- [{gap['code']}] {gap['description']}")
        else:
            sections.append("- nenhuma")
        sections.append("")

        sections.extend(["## Checklist de Prontidao"])
        for item in readiness_checklist:
            marker = "x" if item["completed"] else " "
            sections.append(f"- [{marker}] {item['label']}")

        return "\n".join(sections).strip()

    def _log_execution(self, project_id: int, step: str, message: str, success: bool = True) -> None:
        """Registra toda execucao para fins de auditoria e treinamento."""
        exec_log = AgentExecution(
            project_id=project_id,
            step=step,
            prompt_used=message,
            output_generated=f"Resultado: {message}",
            agent_model="grok-4",
            success=success,
            metadata_json={"timestamp": datetime.now().isoformat()},
        )
        self.db.add(exec_log)
        self.db.commit()


def get_orchestrator(db: Session) -> AgentOrchestrator:
    return AgentOrchestrator(db)
