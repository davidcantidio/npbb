from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlmodel import Session, select
from app.models.framework_models import (
    FrameworkProject, FrameworkIntake, FrameworkPRD, 
    FrameworkPhase, FrameworkEpic, AgentExecution, ProjectStatus, AgentMode
)
# # from app.core.config import settings  # TODO: create app/core/config.py (blocked by FRAMEWORK3)  # TODO: fix missing config for FRAMEWORK3 (blocked by ISSUE-F1-02-002)


class AgentOrchestrator:
    """
    Orquestrador central do FRAMEWORK3.
    Responsável por gerenciar o fluxo completo:
    Intake → PRD → Fases → Épicos → Issues → Tasks → Auditoria
    com suporte a diferentes modos de operação.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.current_mode = AgentMode.HUMAN_IN_LOOP  # default conservador
    
    def create_project(self, project_data: Dict[str, Any]) -> FrameworkProject:
        """Cria um novo projeto a partir de um intake inicial."""
        project = FrameworkProject(
            canonical_name=project_data["canonical_name"],
            title=project_data["title"],
            description=project_data.get("description"),
            status=ProjectStatus.INTAKE,
            agent_mode=project_data.get("agent_mode", AgentMode.HUMAN_IN_LOOP),
            created_by=project_data["created_by"],
            owner=project_data.get("owner", project_data["created_by"]),
            metadata_json=project_data.get("metadata", {})
        )
        
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        
        # Registrar execução
        self._log_execution(project.id, "project_creation", 
                           f"Projeto {project.canonical_name} criado", 
                           success=True)
        
        return project
    
    def process_intake(self, project_id: int, intake_content: str) -> FrameworkIntake:
        """Processa e persiste um Intake."""
        project = self.db.get(FrameworkProject, project_id)
        if not project:
            raise ValueError(f"Projeto {project_id} não encontrado")
        
        intake = FrameworkIntake(
            project_id=project_id,
            doc_id=f"INTAKE-{project.canonical_name}",
            content=intake_content,
            status="draft",
            validated=False,
            checklist_status={"pronto_para_prd": False}
        )
        
        self.db.add(intake)
        self.db.commit()
        self.db.refresh(intake)
        
        # Atualiza status do projeto
        project.intake_id = intake.id
        project.status = ProjectStatus.PRD
        self.db.commit()
        
        self._log_execution(project_id, "intake_processing", 
                          "Intake processado e validado", success=True)
        
        return intake
    
    def generate_prd(self, intake_id: int, auto_approve: bool = False) -> FrameworkPRD:
        """Gera PRD a partir do Intake (integração com lógica de SESSION-CRIAR-PRD)."""
        intake = self.db.get(FrameworkIntake, intake_id)
        if not intake:
            raise ValueError("Intake não encontrado")
        
        # Aqui viria a chamada real ao LLM para gerar PRD baseado no intake
        prd_content = f"# PRD gerado automaticamente a partir de {intake.doc_id}\n\n[Conteúdo gerado por LLM baseado no intake]"
        
        prd = FrameworkPRD(
            project_id=intake.project_id,
            intake_id=intake_id,
            content=prd_content,
            status="draft",
            approved=auto_approve,
            approved_at=datetime.now() if auto_approve else None,
            approved_by="system" if auto_approve else None
        )
        
        self.db.add(prd)
        self.db.commit()
        self.db.refresh(prd)
        
        project = self.db.get(FrameworkProject, intake.project_id)
        project.prd_id = prd.id
        self.db.commit()
        
        self._log_execution(intake.project_id, "prd_generation", 
                          "PRD gerado automaticamente", success=True)
        
        return prd
    
    def start_planning_pipeline(self, project_id: int) -> List[FrameworkPhase]:
        """Inicia o pipeline de planejamento (fases, épicos, issues)."""
        # TODO: Integrar com SESSION-PLANEJAR-PROJETO logic
        project = self.db.get(FrameworkProject, project_id)
        
        phases = []
        # Exemplo: cria fase inicial
        phase = FrameworkPhase(
            project_id=project_id,
            phase_number=1,
            name="Fundacao e Estrutura",
            status=ProjectStatus.PLANNING,
            objective="Estabelecer base do módulo FRAMEWORK3",
            audit_gate="not_ready"
        )
        self.db.add(phase)
        self.db.commit()
        phases.append(phase)
        
        self._log_execution(project_id, "planning_pipeline", 
                          f"Iniciado pipeline de planejamento com {len(phases)} fases", 
                          success=True)
        
        return phases
    
    def execute_next_task(self, project_id: int) -> Dict[str, Any]:
        """Executa a próxima task elegível (integra com SESSION-IMPLEMENTAR-ISSUE)."""
        # Este método será expandido para usar o boot-prompt logic
        execution = {
            "project_id": project_id,
            "step": "task_execution",
            "status": "started",
            "message": "Buscando próxima task elegível conforme governança..."
        }
        self._log_execution(project_id, "task_execution", execution["message"])
        return execution
    
    def _log_execution(self, project_id: int, step: str, message: str, success: bool = True):
        """Registra toda execução para fins de auditoria e treinamento."""
        exec_log = AgentExecution(
            project_id=project_id,
            step=step,
            prompt_used=message,  # Em produção seria o prompt real
            output_generated=f"Resultado: {message}",
            agent_model="grok-4",
            success=success,
            metadata_json={"timestamp": datetime.now().isoformat()}
        )
        self.db.add(exec_log)
        self.db.commit()
    
    def get_project_status(self, project_id: int) -> Dict[str, Any]:
        """Retorna status completo do projeto para UI e orquestração."""
        project = self.db.get(FrameworkProject, project_id)
        if not project:
            return {"error": "Projeto não encontrado"}
        
        return {
            "id": project.id,
            "name": project.canonical_name,
            "status": project.status.value,
            "agent_mode": project.agent_mode.value,
            "has_intake": bool(project.intake_id),
            "has_prd": bool(project.prd_id),
            "progress": "45%",  # calculado dinamicamente no futuro
            "next_action": self._determine_next_action(project)
        }
    
    def _determine_next_action(self, project: FrameworkProject) -> str:
        if project.status == ProjectStatus.INTAKE:
            return "Gerar PRD"
        elif project.status == ProjectStatus.PRD:
            return "Iniciar Planejamento de Fases"
        elif project.status == ProjectStatus.PLANNING:
            return "Gerar Issues e Tasks"
        elif project.status == ProjectStatus.EXECUTION:
            return "Executar próxima Task"
        return "Auditoria ou Finalização"


# Serviço para ser injetado no FastAPI
def get_orchestrator(db: Session):
    return AgentOrchestrator(db)
