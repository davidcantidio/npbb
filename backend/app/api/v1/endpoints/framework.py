from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Optional

from app.db.session import get_db
from app.models.framework_models import (
    FrameworkIntake,
    FrameworkProject,
)
from app.services.framework_orchestrator import AgentOrchestrator
from app.schemas.framework import FrameworkIntakeGenerateRequest, FrameworkIntakeRead

router = APIRouter(prefix="/framework", tags=["framework"])


def get_orchestrator(db: Session = Depends(get_db)) -> AgentOrchestrator:
    """Dependency to get orchestrator instance."""
    return AgentOrchestrator(db)


@router.post("/projects/", response_model=None)
def create_framework_project(
    project_in: dict,
    db: Session = Depends(get_db),
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """Cria um novo projeto no sistema FRAMEWORK3."""
    try:
        project = orchestrator.create_project(project_in)
        return {"id": project.id, "canonical_name": project.canonical_name, "title": project.title, "status": project.status.value}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao criar projeto: {str(e)}"
        )


@router.get("/projects/{project_id}/status")
def get_project_status(
    project_id: int,
    db: Session = Depends(get_db),
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """Retorna status detalhado do projeto (para UI)."""
    status = orchestrator.get_project_status(project_id)
    if "error" in status:
        raise HTTPException(status_code=404, detail=status["error"])
    return status


@router.post("/projects/{project_id}/intake", response_model=FrameworkIntakeRead)
def submit_intake(
    project_id: int,
    intake_in: FrameworkIntakeGenerateRequest,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
):
    """Submete um Intake para processamento."""
    try:
        return orchestrator.process_intake(project_id, intake_in)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/projects/{project_id}/prd/generate")
def generate_prd(
    project_id: int,
    auto_approve: bool = False,
    db: Session = Depends(get_db),
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """Gera PRD a partir do intake (integra com lógica de governança)."""
    # Buscar intake mais recente do projeto
    intake = db.exec(
        select(FrameworkIntake)
        .where(FrameworkIntake.project_id == project_id)
        .order_by(FrameworkIntake.created_at.desc())
    ).first()
    
    if not intake:
        raise HTTPException(status_code=404, detail="Intake não encontrado para este projeto")
    
    prd = orchestrator.generate_prd(intake.id, auto_approve)
    return {"message": "PRD gerado", "prd_id": prd.id, "auto_approved": auto_approve}


@router.post("/projects/{project_id}/plan")
def start_planning(
    project_id: int,
    db: Session = Depends(get_db),
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """Inicia o pipeline de planejamento (fases, épicos, etc)."""
    phases = orchestrator.start_planning_pipeline(project_id)
    return {
        "message": "Pipeline de planejamento iniciado",
        "phases_created": len(phases),
        "next_step": "Gerar épicos e issues"
    }


@router.get("/projects")
def list_projects(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lista todos os projetos do framework."""
    statement = select(FrameworkProject)
    if status:
        statement = statement.where(FrameworkProject.status == status)
    
    projects = db.exec(statement).all()
    return projects
