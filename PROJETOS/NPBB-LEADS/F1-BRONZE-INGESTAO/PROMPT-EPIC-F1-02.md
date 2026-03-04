# Guia: Como usar os Prompt Files
#
# Cada EPIC tem um arquivo PROMPT-EPIC-FN-NN.md ao lado.
# Fluxo: abrir o arquivo → Ctrl+A → Ctrl+C → colar no Cloud Agent (Ctrl+E).
# Um agente por EPIC. Uma branch por agente.
#
# Estrutura:
# PROJETOS/NPBB-LEADS/
# ├── F1-BRONZE-INGESTAO/
# │   ├── PROMPT-EPIC-F1-01.md   ← já disparado
# │   └── PROMPT-EPIC-F1-02.md   ← este arquivo
# ├── F2-SILVER-MAPEAMENTO/
# │   └── PROMPT-EPIC-F2-01.md
# └── F3-GOLD-PIPELINE/
#     └── PROMPT-EPIC-F3-01.md

---

Você é um engenheiro sênior trabalhando no projeto npbb
(FastAPI + SQLModel + React/Vite + PostgreSQL 16).

Leia obrigatoriamente estes arquivos antes de escrever qualquer código:
1. AGENTS.md
2. PROJETOS/NPBB-LEADS/PRD-NPBB-LEADS.md
3. PROJETOS/NPBB-LEADS/F1-BRONZE-INGESTAO/EPIC-F1-02-UNIFICACAO-UI-IMPORTACAO.md
4. backend/app/routers/leads.py
5. frontend/src/ — identifique as rotas de importação existentes
6. frontend/src/pages/leads/ — entenda os componentes de leads atuais

Implemente na ordem:
1. NPBB-F1-02-001: Componente ImportacaoStepper (Step 1 — metadados + upload)
2. NPBB-F1-02-002: Step 2 — preview de colunas (endpoint backend + componente)
3. NPBB-F1-02-003: Remover / redirecionar rota "Importação Avançada"

Regras não negociáveis:
- Sempre use PYTHONPATH=/workspace:/workspace/backend
- Testes backend: TESTING=true SECRET_KEY=ci-secret-key python -m pytest -q
- Não remover código de backend de importação existente — apenas UI
- Não quebrar os 283+ testes existentes
- Seguir exatamente os Critérios de Aceitação de cada issue

Ao finalizar:
- Atualize o status das issues para ✅ em EPIC-F1-02-UNIFICACAO-UI-IMPORTACAO.md
- Abra PR com título: "feat: UI de importação unificada Bronze step 1+2 (EPIC-F1-02)"
- Corpo do PR: checklist de Critérios de Aceitação com status de cada item
