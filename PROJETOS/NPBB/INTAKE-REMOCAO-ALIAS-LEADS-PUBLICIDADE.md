---
doc_id: "INTAKE-REMOCAO-ALIAS-LEADS-PUBLICIDADE.md"
version: "1.0"
status: "approved"
owner: "PM"
last_updated: "2026-04-23"
project: "NPBB"
intake_kind: "structural-remediation"
source_mode: "derived"
origin_project: "NPBB"
origin_phase: "FEATURE-6-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS"
origin_audit_id: "remove-legacy-alias"
origin_report_path: "plano_organizacao_import.md"
product_type: "platform-capability"
delivery_surface: "backend-module"
business_domain: "eventos-e-leads"
criticality: "alta"
data_sensitivity: "lgpd"
integrations:
  - "backend"
  - "tests"
  - "docs-governance"
change_type: "limpeza-estrutural"
audit_rigor: "elevated"
---

# INTAKE - Remocao do alias leads_publicidade

> Intake derivado da `FEATURE-6-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS`
> para remover a compatibilidade temporaria `app.modules.leads_publicidade`
> depois da migracao dos consumidores ativos para `app.modules.lead_imports`.

## 0. Rastreabilidade de Origem

- projeto de origem: `NPBB`
- unidade de origem: `plano_organizacao_import.md`
- decisao de origem: `FEATURE-6-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS`
- caminho real aprovado: `app.modules.lead_imports`
- caminho legado a remover: `app.modules.leads_publicidade`

## 1. Resumo Executivo

- nome curto da iniciativa: remocao alias leads publicidade
- tese em 1 frase: remover o pacote legado de compatibilidade depois de busca
  sem consumidores ativos
- valor esperado:
  - eliminar ambiguidade estrutural no backend
  - impedir novos imports pelo nome antigo
  - manter a rodada limitada a limpeza interna sem alterar ETL funcional

## 2. Problema ou Oportunidade

- problema atual: `backend/app/modules/leads_publicidade` ainda existe como
  alias temporario, mesmo apos `app.modules.lead_imports` virar o pacote real
- evidencia: a busca em codigo ativo nao encontra consumidores fora dos shims
  de compatibilidade e do teste dedicado de compatibilidade
- oportunidade: fechar a janela de migracao com uma remocao pequena e
  validada por testes focados

## 3. Escopo Inicial

### Dentro

- confirmar ausencia de consumidores ativos do caminho legado
- remover `backend/app/modules/leads_publicidade/**`
- remover `backend/tests/test_lead_imports_compat.py`
- registrar a rodada na governanca `FEATURE-7`
- atualizar `plano_organizacao_import.md`

### Fora

- alterar comportamento de ETL, persistencia, validadores ou merge policy
- alterar contratos HTTP, schemas ou rotas publicas
- alterar frontend, dashboard, `lead_pipeline/` ou `core/leads_etl/`
- reescrever docs/governanca historicas apenas para trocar referencias antigas
- criar teste novo que preserve referencia ativa ao caminho legado

## 4. Interfaces e Contratos que Devem Permanecer Estaticos

- caminho backend suportado: `app.modules.lead_imports.*`
- rotas sob `/leads` permanecem sem mudanca de contrato
- scripts atuais devem continuar executando com o mesmo comportamento
- regras de validacao, persistencia, merge e DQ permanecem inalteradas

## 5. Riscos Relevantes

- consumidor legado nao mapeado ainda importar `app.modules.leads_publicidade`
- monkeypatch por string antigo existir fora do teste dedicado
- misturar esta limpeza backend com mudancas frontend pendentes no worktree
- reabrir ETL funcional por acidente

## 6. Resultado Esperado e Metricas de Sucesso

- `backend/app/modules/leads_publicidade` deixa de existir
- `backend/tests/test_lead_imports_compat.py` deixa de existir
- `app.modules.lead_imports` permanece importavel e usado por consumidores
  ativos
- testes focados de ETL/importacao passam
- referencias restantes a `leads_publicidade` ficam restritas a historico em
  docs, governanca e plano operacional

## 7. Follow-ups Deliberadamente Adiados

- mover outros slices frontend de leads
- reabrir importacao/ETL funcional
- remover wrappers legados frontend de `pages/*` e `hooks/*`
