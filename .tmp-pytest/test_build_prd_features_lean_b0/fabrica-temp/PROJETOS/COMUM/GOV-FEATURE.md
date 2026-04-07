---
doc_id: "GOV-FEATURE.md"
version: "1.4"
status: "active"
owner: "PM"
last_updated: "2026-04-04"
---

# GOV-FEATURE

## Objetivo

Definir o contrato normativo do manifesto canonico de feature:
`PROJETOS/<PROJETO>/features/FEATURE-<N>-<SLUG>/FEATURE-<N>.md`.

Markdown versionado em Git continua sendo a forma canonica do backlog.
Read models apenas espelham paths e metadados.

## Artefato canonico

- uma feature ativa possui um manifesto `FEATURE-<N>.md`
- o manifesto vive em `features/FEATURE-<N>-<SLUG>/`
- a etapa `PRD -> Features` cria a feature; o PRD nao carrega esse backlog
- a feature organiza um recorte entregavel do PRD sem substituir US ou tasks

## Identificadores e paths

| Forma | Exemplo | Uso canonico |
|-------|---------|--------------|
| `feature_key` | `FEATURE-1` | identificador curto do manifesto e de `depende_de` |
| pasta canonica | `FEATURE-1-DOMINIO-COMPARTILHADO` | path no repositorio |
| `feature_slug` | `DOMINIO-COMPARTILHADO` | parte humana/estavel da pasta apos `FEATURE-<N>-` |

Regras:

- `feature_key` e sempre `FEATURE-<N>`
- a pasta sempre segue `FEATURE-<N>-<SLUG>`
- `feature_slug` deve ser compativel com a pasta e permanecer estavel
- paths e referencias devem continuar coerentes apos qualquer renomeacao

## Conteudo obrigatorio do manifesto

O manifesto precisa conter, de forma objetiva e auditavel:

| Area | Minimo exigido |
|------|----------------|
| Rastreabilidade | projeto, `prd_path`, `intake_path` quando existir, `depende_de`, `agent_id` opcional quando vier da trilha lean |
| Evidencia no PRD | pelo menos um par `secao / ancora` + `sintese objetiva` |
| Objetivo de negocio | problema que a feature resolve e resultado esperado |
| Comportamento esperado | lista do que o usuario ou operador passa a conseguir fazer |
| Dependencias entre features | apenas `FEATURE-<N>` do mesmo projeto |
| Criterios de aceite | criterios verificaveis da feature |
| Riscos especificos | riscos proprios do recorte entregue |
| Impactos por camada | `Banco`, `Backend`, `Frontend`, `Testes`, `Observabilidade` |

O manifesto pode incluir scaffold operacional adicional do repositorio
(`status`, `audit_gate`, tabela de US e referencias), mas isso nao substitui os
campos acima.

Quando a feature vier da trilha lean canonica (default com provider ou modo
`--proposal-file`), o renderer deve:

- persistir `agent_id` apenas como metadata opaca de rastreabilidade
- preencher `Impactos por camada` a partir de `layer_impacts.<camada>.impact`
  e `layer_impacts.<camada>.detail`
- manter `agent_id` sem qualquer semantica de provider ou runtime

## Dependencias entre features

- `depende_de` usa apenas `feature_key` curto, por exemplo `FEATURE-1`
- dependencias devem apontar para features do mesmo projeto
- ciclos devem ser evitados
- se houver dependencia bloqueante, ela precisa aparecer no frontmatter e no
  corpo do manifesto

## Fronteira com PRD, US e Tasks

- a feature nao substitui o PRD nem repete o escopo global do projeto
- a feature nao substitui user story
- a feature nao substitui task
- a secao `User Stories (rastreabilidade)` e apenas indice downstream depois da
  etapa `Feature -> User Stories`
- criterios Given / When / Then vivem nas US, nao no manifesto de feature

## Prontidao para `Feature -> User Stories`

Antes de decompor a feature em US:

- evidencia no PRD esta preenchida
- objetivo de negocio esta claro
- comportamento esperado esta listado
- criterios de aceite sao verificaveis
- impactos por camada permitem fatiar a implementacao sem ambiguidade grave
- dependencias entre features estao declaradas

Se esses pontos nao estiverem presentes, a resposta correta e `BLOQUEADO`.

## Relacao com docs nucleares

| Documento | Papel |
|-----------|-------|
| `GOV-PRD.md` | contrato do insumo PRD |
| `TEMPLATE-FEATURE.md` | shape Markdown canonico do manifesto |
| `PROMPT-PRD-PARA-FEATURES.md` | contrato operacional de `PRD -> Features` |
| `PROMPT-FEATURE-PARA-USER-STORIES.md` | decomposicao da feature em US |
| `GOV-USER-STORY.md` | contrato da US |
| `GOV-SCRUM.md` | estados operacionais do fluxo |
