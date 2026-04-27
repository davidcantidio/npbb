---
doc_id: "PRD-DECISAO-SHELL-IMPORTACAO-LEADS.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-23"
project: "NPBB"
intake_kind: "structural-remediation"
source_mode: "derived"
origin_project: "NPBB"
origin_phase: "FEATURE-8-REMOCAO-WRAPPERS-FRONTEND-LEADS"
origin_audit_id: "plano_organizacao_import"
origin_report_path: "plano_organizacao_import.md"
product_type: "platform-capability"
delivery_surface: "frontend-module"
business_domain: "eventos-e-leads"
criticality: "alta"
data_sensitivity: "lgpd"
integrations:
  - "frontend"
  - "docs-governance"
change_type: "decisao-estrutural"
audit_rigor: "elevated"
---

# PRD - Decisao sobre shell de importacao de leads

> Origem:
> [INTAKE-DECISAO-SHELL-IMPORTACAO-LEADS.md](INTAKE-DECISAO-SHELL-IMPORTACAO-LEADS.md)

## 0. Rastreabilidade

- intake de origem:
  [INTAKE-DECISAO-SHELL-IMPORTACAO-LEADS.md](INTAKE-DECISAO-SHELL-IMPORTACAO-LEADS.md)
- data de criacao: `2026-04-23`
- base estrutural preservada:
  `FEATURE-8-REMOCAO-WRAPPERS-FRONTEND-LEADS`
- decisao operacional de suporte:
  `plano_organizacao_import.md`

## 1. Resumo Executivo

- nome do mini-projeto: decisao shell importacao leads
- tese em 1 frase: manter `/leads/importar` no local atual nesta rodada e
  documentar a fronteira para uma migracao parcial futura
- valor esperado:
  - reduzir risco de refactor amplo no shell de importacao
  - preservar comportamento de upload, Bronze, ETL, mapeamento e pipeline
  - criar base objetiva para uma feature posterior de migracao parcial

## 2. Objetivo do PRD

Executar uma rodada documental para decidir a fronteira do shell frontend de
importacao de leads, registrar dependencias reais e impedir alteracoes
funcionais enquanto o escopo de importacao/ETL continua congelado.

## 3. Requisitos Funcionais e Estruturais

1. When a decisao da `FEATURE-9` for registrada, the system shall manter
   `frontend/src/pages/leads/ImportacaoPage.tsx` como shell canonico de
   `/leads/importar`.
2. When o inventario for registrado, the system shall listar
   `frontend/src/pages/leads/importacao/**` como submodulo local atual do shell.
3. When o inventario for registrado, the system shall listar `MapeamentoPage`,
   `BatchMapeamentoPage` e `PipelineStatusPage` como telas acopladas ao shell.
4. When o inventario for registrado, the system shall listar os testes de
   importacao, mapeamento e pipeline que ainda importam de
   `frontend/src/pages/leads`.
5. Where future frontend organization is planned, the system shall tratar
   `frontend/src/features/leads/importacao` como destino preferencial apenas
   para uma feature posterior.
6. The system shall not move files, change behavior, update routes, alter
   backend, change contracts, touch ETL or modify pipeline code in this rodada.

## 4. Requisitos Nao Funcionais

- seguranca/LGPD: nenhuma nova exposicao de dados sera criada
- compatibilidade: `/leads/importar` deve permanecer funcionalmente igual
- rollback: a rodada e documental e revertivel pela remocao dos artefatos de
  governanca e do trecho correspondente no plano
- testabilidade: buscas de fronteira devem comprovar que o shell permanece no
  local atual; suite funcional nao e obrigatoria sem diff funcional

## 5. Escopo

### Dentro

- governanca da decisao
- inventario de dependencias do shell
- atualizacao do plano operacional
- registro de validacoes de baseline

### Fora

- migracao de arquivos frontend
- alteracao de testes de importacao
- backend, schemas, contratos HTTP, rotas publicas, ETL, Bronze, mapeamento,
  pipeline, `lead_pipeline/` e `core/leads_etl/`
- dashboard de conversao

## 6. Criterios de Aceite

- Given a rota `/leads/importar`,
  when `AppRoutes.tsx` for revisado,
  then o lazy import continua apontando para `../pages/leads/ImportacaoPage`.
- Given o shell atual,
  when a governanca da `FEATURE-9` for lida,
  then a decisao explicita e manter o shell em `frontend/src/pages/leads` nesta
  rodada.
- Given os subfluxos de importacao,
  when o inventario for lido,
  then `MapeamentoPage`, `BatchMapeamentoPage` e `PipelineStatusPage` aparecem
  como acoplamentos que bloqueiam uma migracao direta.
- Given o freeze de importacao/ETL,
  when a rodada terminar,
  then nenhum arquivo funcional de frontend, backend, ETL ou pipeline foi
  alterado pela feature.
- Given as mudancas locais de dashboard preexistentes,
  when a rodada terminar,
  then elas permanecem preservadas e fora do escopo.

## 7. Validacao Minima Obrigatoria

- `git status --short`
- `git log -1 --oneline`
- `rg -n "ImportacaoPage|pages/leads/importacao|PipelineStatusPage|MapeamentoPage|BatchMapeamentoPage" frontend/src`
- `rg -n "app\\.modules\\.leads_publicidade|leads_publicidade" backend/app backend/scripts backend/tests`

Como esta rodada e documental, `typecheck` e suites funcionais nao sao
obrigatorios. Se qualquer arquivo funcional entrar no diff, a rodada deve parar
e abrir gate proprio.

## 8. Decomposicao Aprovada

- `FEATURE-9-DECISAO-SHELL-IMPORTACAO-LEADS`
  - `US-9-01`: decidir shell de importacao de leads

## 9. Checklist de Prontidao

- [x] decisao escolhida: manter shell em `frontend/src/pages/leads`
- [x] migracao funcional explicitamente fora do escopo
- [x] backend, ETL, Bronze, mapeamento e pipeline fora do escopo
- [x] proxima migracao condicionada a feature posterior
- [x] rollback documental definido
