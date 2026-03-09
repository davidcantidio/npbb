---
doc_id: "SPEC-ANTI-MONOLITO.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-09"
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

Referencia observada no projeto ativo `dashboard-leads-etaria`:

- frontend dashboard: maior arquivo funcional localizado com `293` linhas
- backend dashboard: maior arquivo funcional localizado com `380` linhas

Com base nisso, o threshold de aviso inicia acima do maior arquivo funcional do
dashboard e o threshold bloqueante fica reservado para outliers claros.

## Thresholds por Arquivo

| Metrica | Aviso | Bloqueante |
|---|---|---|
| linhas de codigo logico por arquivo | `> 400` | `> 600` |
| exports/conceitos publicos distintos no mesmo arquivo | `> 7` | `> 12` |
| dominios de import distintos no mesmo arquivo | `> 5` | `> 7` |

## Thresholds por Funcao

| Metrica | Aviso | Bloqueante |
|---|---|---|
| linhas por funcao | `> 60` | `> 100` |
| niveis de aninhamento | `> 3` | `> 4` |
| parametros | `> 6` | `> 8` |
| ramos condicionais relevantes no mesmo corpo | `> 10` | `> 15` |

## Aplicacao por Linguagem

### TypeScript/React

- conte componentes, hooks, helpers exportados e builders visiveis como `exports`
- conte dominios por raiz de import funcional, nao por arquivo individual
- componentes com JSX muito extenso entram no threshold de arquivo, mesmo com funcoes pequenas

### Python

- conte funcoes top-level, classes e helpers publicos como conceitos distintos
- modulos de servico e router com muitas regras de negocio devem ser medidos por arquivo e por funcao
- validadores ou schemas declarativos podem ser rebaixados manualmente quando o codigo for majoritariamente estrutural

## Mapeamento para Auditoria

- cruzar um threshold de aviso gera achado `medium` por padrao
- cruzar um threshold bloqueante gera achado `high` por padrao
- `hold` continua dependente do contexto, mas thresholds bloqueantes exigem justificativa explicita para nao bloquear
- quando houver trend positiva clara entre rodadas, registrar na tabela de complexidade estrutural do relatorio

## Excecoes Permitidas

- arquivos gerados automaticamente
- snapshots ou fixtures de teste
- barrels sem logica
- schemas declarativos extensos, desde que sem concentracao de regra de negocio

Toda excecao deve ser justificada no relatorio de auditoria.
