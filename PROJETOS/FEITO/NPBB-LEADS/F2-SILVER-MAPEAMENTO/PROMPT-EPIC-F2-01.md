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
2. PROJETOS/NPBB-LEADS/PRD-NPBB-LEADS.md — seções "Modelo de Dados" e "Fluxo Geral"
3. PROJETOS/NPBB-LEADS/F2-SILVER-MAPEAMENTO/EPIC-F2-01-MAPEAMENTO-E-PERSISTENCIA-SILVER.md
4. PROJETOS/lead_pipeline/constants.py — HEADER_SYNONYMS e REQUIRED_COLUMNS
5. PROJETOS/lead_pipeline/normalization.py — normalize_header()
6. backend/app/models/ — modelos LeadBatch, LeadSilver, LeadColumnAlias (criados no F1)
7. backend/app/routers/leads.py

Implemente na ordem:
1. NPBB-F2-01-001: Serviço de sugestão + endpoint GET /leads/batches/{id}/colunas
2. NPBB-F2-01-002: Endpoint POST /leads/batches/{id}/mapear + persistência Silver
3. NPBB-F2-01-003: UI de mapeamento de colunas (MapeamentoPage.tsx)

Regras não negociáveis:
- Sempre use PYTHONPATH=/workspace:/workspace/backend
- Testes: TESTING=true SECRET_KEY=ci-secret-key python -m pytest -q
- Importar HEADER_SYNONYMS e normalize_header DIRETAMENTE de lead_pipeline
  (não copiar o código — usar o módulo via PYTHONPATH)
- Silver preserva dado bruto — nenhuma normalização aqui
- Não quebrar os 283+ testes existentes
- Seguir exatamente os Critérios de Aceitação de cada issue

Ao finalizar:
- Atualize o status das issues para ✅ em EPIC-F2-01-MAPEAMENTO-E-PERSISTENCIA-SILVER.md
- Abra PR com título: "feat: Silver — mapeamento de colunas + persistência (EPIC-F2-01)"
- Corpo do PR: checklist de Critérios de Aceitação com status de cada item
