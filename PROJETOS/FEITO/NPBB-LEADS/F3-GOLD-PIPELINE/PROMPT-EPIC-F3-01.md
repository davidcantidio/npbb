# Guia: Como usar os Prompt Files
#
# Cada EPIC tem um arquivo PROMPT-EPIC-FN-NN.md ao lado.
# Fluxo: abrir o arquivo → Ctrl+A → Ctrl+C → colar no Cloud Agent (Ctrl+E).
# Um agente por EPIC. Uma branch por agente.

---

Você é um engenheiro sênior trabalhando no projeto npbb
(FastAPI + SQLModel + React/Vite + PostgreSQL 16).

Leia obrigatoriamente estes arquivos antes de escrever qualquer código:
1. AGENTS.md
2. PROJETOS/NPBB-LEADS/PRD-NPBB-LEADS.md — seções "Fluxo Geral" e "Modelo de Dados"
3. PROJETOS/NPBB-LEADS/F3-GOLD-PIPELINE/EPIC-F3-01-PIPELINE-TRATAMENTO-GOLD.md
4. PROJETOS/lead_pipeline/pipeline.py — run_pipeline(), PipelineConfig, PipelineResult
5. PROJETOS/lead_pipeline/constants.py — REQUIRED_COLUMNS, FINAL_FILENAME
6. PROJETOS/lead_pipeline/contracts.py — validate_databricks_contract()
7. backend/app/models/ — LeadBatch, LeadSilver, Lead (modelo Gold existente)
8. backend/app/routers/leads.py

Implemente na ordem:
1. NPBB-F3-01-001: Serviço lead_pipeline_service.py (materializar Silver → executar pipeline → inserir Gold)
2. NPBB-F3-01-002: Endpoint POST /leads/batches/{id}/executar-pipeline (background task)
3. NPBB-F3-01-003: UI de status do pipeline + polling + relatório (PipelineStatusPage.tsx)

Regras não negociáveis:
- Sempre use PYTHONPATH=/workspace:/workspace/backend
- Testes: TESTING=true SECRET_KEY=ci-secret-key python -m pytest -q
- run_pipeline() DEVE rodar em thread pool via loop.run_in_executor — não bloquear o event loop
- FAIL no pipeline: NENHUM lead inserido na tabela leads, stage permanece silver
- Arquivos temporários em /tmp/npbb_pipeline/{batch_id}/ limpos após execução
- Importar run_pipeline diretamente de lead_pipeline (PYTHONPATH já configurado)
- Não quebrar os 283+ testes existentes
- Seguir exatamente os Critérios de Aceitação de cada issue

Ao finalizar:
- Atualize o status das issues para ✅ em EPIC-F3-01-PIPELINE-TRATAMENTO-GOLD.md
- Abra PR com título: "feat: Gold — pipeline ETL + promoção de leads (EPIC-F3-01)"
- Corpo do PR: checklist de Critérios de Aceitação + métricas do pipeline (raw/valid/discarded)
