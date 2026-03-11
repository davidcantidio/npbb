---
doc_id: "SPEC-ANTI-MONOLITO.md"
version: "1.2"
status: "active"
owner: "PM"
last_updated: "2026-03-11"
---

# SPEC-ANTI-MONOLITO

## Objetivo

Definir thresholds objetivos para os achados `monolithic-file` e
`monolithic-function`, reduzindo julgamento subjetivo em auditorias.

## Escopo

- linguagens cobertas nesta versao: `TypeScript/React` e `Python`
- uso principal: auditoria de fase, follow-up estrutural e intake de remediacao
- gerado automaticamente, arquivos declarativos simples e barrels puros podem ser reavaliados manualmente

## Calibracao Inicial

Calibracao minima validada em `2026-03-11` usando o codigo atual do repositorio
e a trilha documental do projeto ativo `dashboard-leads-etaria`.

Amostra considerada, excluindo testes, docs arquivadas, arquivos gerados e
artefatos de build:

- backend dashboard:
  - `backend/app/services/dashboard_service.py` com `381` linhas
  - `backend/app/schemas/dashboard.py` com `169` linhas
  - `backend/app/routers/dashboard.py` com `94` linhas
- frontend dashboard:
  - `frontend/src/components/dashboard/EventsAgeTable.tsx` com `283` linhas
  - `frontend/src/components/dashboard/AgeDistributionChart.tsx` com `224` linhas
  - `frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx` com `175` linhas
  - `frontend/src/components/dashboard/ConsolidatedPanel.tsx` com `158` linhas
  - `frontend/src/components/dashboard/AgeAnalysisFilters.tsx` com `139` linhas

Sinais observados na amostra:

- maior arquivo funcional backend: `381` linhas
- maior arquivo funcional frontend: `283` linhas
- maior funcao Python observada: `build_age_analysis` com `53` linhas em
  `backend/app/services/dashboard_service.py`
- componentes React como `LeadsAgeAnalysisPage`, `ConsolidatedPanel` e
  `AgeAnalysisFilters` ultrapassam `60` linhas quando contados de forma bruta,
  mas o excedente observado vem majoritariamente da arvore declarativa de JSX,
  nao de branching pesado ou profundidade estrutural anormal

Decisao de calibracao:

- thresholds numericos `warn/block` foram mantidos
- a regra de interpretacao para `TypeScript/React` foi refinada para evitar
  falso positivo de `monolithic-function` em componentes declarativos
- o threshold de aviso continua acima do maior arquivo funcional observado no
  dashboard, e o threshold bloqueante permanece reservado para outliers claros

## Niveis Operacionais

- `warn`: threshold que exige registro explicito de atencao estrutural no relatorio
  de auditoria, mesmo quando o gate nao for bloqueado
- `block`: threshold que exige justificativa explicita para nao bloquear o gate
  com achado estrutural

Nao existe terceiro nivel implicito nesta versao. Toda avaliacao operacional
deve usar apenas `warn` ou `block`.

## Dimensoes Estruturais Obrigatorias

Esta versao cobre `TypeScript/React` e `Python` nas mesmas duas dimensoes
estruturais obrigatorias:

- dimensao de arquivo: concentracao de codigo, conceitos publicos e dominios de import
- dimensao de funcao: concentracao de logica, profundidade, superficie de chamada e branching

As tabelas abaixo sao a fonte canonica de `warn` e `block` para cada dimensao.

## Thresholds por Arquivo

| Metrica | warn | block |
|---|---|---|
| linhas de codigo logico por arquivo | `> 400` | `> 600` |
| exports/conceitos publicos distintos no mesmo arquivo | `> 7` | `> 12` |
| dominios de import distintos no mesmo arquivo | `> 5` | `> 7` |

## Thresholds por Funcao

| Metrica | warn | block |
|---|---|---|
| linhas por funcao | `> 60` | `> 100` |
| niveis de aninhamento | `> 3` | `> 4` |
| parametros | `> 6` | `> 8` |
| ramos condicionais relevantes no mesmo corpo | `> 10` | `> 15` |

## Aplicacao por Linguagem

Todos os thresholds `warn` e `block` desta versao valem para `TypeScript/React`
e `Python`. A diferenca entre as linguagens esta apenas em como interpretar cada
metrica, conforme as regras abaixo.

### TypeScript/React

- conte componentes, hooks, helpers exportados e builders visiveis como `exports`
- conte dominios por raiz de import funcional, nao por arquivo individual
- normalize imports locais do mesmo modulo funcional como um unico dominio
- componentes com JSX muito extenso entram primeiro no threshold de arquivo
- na dimensao de funcao, priorize a logica imperativa do componente
  (hooks, handlers, helpers e branching relevante); JSX declarativo extenso, por
  si so, nao deve classificar `monolithic-function`

### Python

- conte funcoes top-level, classes e helpers publicos como conceitos distintos
- modulos de servico e router com muitas regras de negocio devem ser medidos por arquivo e por funcao
- validadores ou schemas declarativos podem ser rebaixados manualmente quando o codigo for majoritariamente estrutural

## Mapeamento para Auditoria

- cruzar um threshold `warn` gera achado `medium` por padrao
- cruzar um threshold `block` gera achado `high` por padrao
- cruzar `block` exige justificativa explicita para nao bloquear o gate
- o auditor nao deve inferir thresholds ou niveis adicionais fora desta tabela
- quando houver trend positiva clara entre rodadas, registrar na tabela de complexidade estrutural do relatorio

## Excecoes Permitidas

- arquivos gerados automaticamente
- snapshots ou fixtures de teste
- barrels sem logica
- schemas declarativos extensos, desde que sem concentracao de regra de negocio

Toda excecao deve ser justificada no relatorio de auditoria.
