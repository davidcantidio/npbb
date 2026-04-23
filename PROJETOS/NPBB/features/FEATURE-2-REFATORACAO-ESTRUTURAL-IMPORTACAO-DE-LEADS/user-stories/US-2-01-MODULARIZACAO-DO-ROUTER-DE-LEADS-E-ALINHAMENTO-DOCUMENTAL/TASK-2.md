---
doc_id: "TASK-2.md"
user_story_id: "US-2-01-MODULARIZACAO-DO-ROUTER-DE-LEADS-E-ALINHAMENTO-DOCUMENTAL"
task_id: "T2"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-22"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "docs/WORKFLOWS.md"
  - "docs/MANUAL-NPBB.md"
  - "docs/tela-inicial/menu/Dashboard/leads_dashboard.md"
tdd_aplicavel: false
---

# T2 - Atualizar docs operacionais e registrar divergencias reais de rota

## objetivo

Alinhar a documentacao operacional com a superficie real do produto para evitar
drift entre shell canonico, redirects legados e dashboard roteado.

## passos_atomicos

1. registrar `/leads/importar` como shell canonico
2. documentar `/leads/mapeamento` e `/leads/pipeline` como redirects legados
3. registrar `/dashboard/leads/analise-etaria` como rota de tela atual
4. explicitar que `/dashboard/leads/relatorio` continua sendo API/script

## comandos_permitidos

- `rg -n "/leads/importar|/leads/mapeamento|/leads/pipeline|/dashboard/leads" docs`

## stop_conditions

- parar se a doc precisar afirmar uma tela ou fluxo que nao existe no produto
