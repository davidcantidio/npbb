---
doc_id: "GOV-PRD.md"
version: "2.2"
status: "active"
owner: "PM"
last_updated: "2026-04-03"
---

# GOV-PRD

## Objetivo

Definir o contrato normativo do `PRD-<PROJETO>.md` como insumo da etapa
`PRD -> Features`.

O PRD e um artefato estrategico e de produto. Ele descreve problema, objetivo,
escopo, restricoes, dependencias, riscos, arquitetura geral e rollout do
projeto. A decomposicao entregavel em `FEATURE-*`, `US-*` e `TASK-*` acontece
depois, em etapas proprias do pipeline.

Markdown versionado em Git continua sendo a forma canonica do PRD. Indices
derivados apenas espelham metadados.

## Fronteira normativa do PRD

- Todo projeto ativo referencia um PRD principal `PRD-<PROJETO>.md`, com
  rastreabilidade ao intake.
- `Especificacao Funcional` define o `o que / por que`.
- `Plano Tecnico` define o `como`.
- Se houver conflito, `Especificacao Funcional` prevalece e o `Plano Tecnico`
  deve ser revisto.
- A etapa `PRD -> Features` usa o PRD como insumo; o PRD nao substitui
  manifesto de feature, user story, task ou relatorio de auditoria.

## Conteudo obrigatorio para elegibilidade

Para estar apto a `PRD -> Features`, o PRD precisa cobrir de forma verificavel:

| Area | Minimo exigido |
|------|----------------|
| Problema / oportunidade | contexto, evidencia, custo de nao agir, por que agora |
| Objetivo e valor | resumo executivo e resultado de negocio esperado |
| Publico e operadores | quem usa, quem opera, quem aprova ou patrocina |
| Jobs to be done | trabalho principal e trabalho atual a ser substituido |
| Escopo | dentro, fora e nao-objetivos |
| Metricas | leading, lagging e criterio minimo de sucesso |
| Restricoes e guardrails | tecnicas, operacionais, legais/compliance, prazo, marca/design |
| Dependencias e integracoes | sistemas, dados de entrada e dados de saida |
| Hipoteses congeladas | lacunas resolvidas, hipoteses aceitas, dependencias pendentes, riscos de interpretacao |
| Arquitetura geral | visao unificada de backend, frontend, dados, observabilidade e auth quando relevante |
| Riscos globais | produto, tecnico, operacional, dados e adocao |
| Rollout | estrategia de deploy, comunicacao, treinamento e suporte pos-launch |
| Revisoes e auditorias | gates em nivel de projeto, sem backlog detalhado no PRD |

Para decomposicao lean, o PRD tambem precisa oferecer evidencia minima em:

- escopo
- metricas
- restricoes / guardrails
- dependencias / integracoes
- rollout
- riscos globais

`SPEC-LEITURA-MINIMA-EVIDENCIA.md` se aplica como politica de leitura desta
etapa. Ela nao amplia o escopo do PRD.

## Conteudo proibido no PRD

Backlog estruturado dentro do PRD invalida a decomposicao `PRD -> Features`.
Os itens abaixo sao proibidos no corpo normativo do PRD:

- IDs de feature como `FEATURE-1`, `FEATURE-2` ou equivalentes
- IDs de user story como `US-1-01`, `US-2.3` ou equivalentes
- tabelas, listas ou catalogos de backlog por feature ou por user story
- criterios de aceite por feature dentro do PRD
- roadmap detalhado em granularidade de feature, user story ou task

O PRD pode citar capacidades ou temas em linguagem de alto nivel, desde que:

- nao use IDs de backlog
- nao descreva aceite por feature
- nao substitua manifestos `FEATURE-*.md`

## Checklist de prontidao para `PRD -> Features`

- [ ] Intake referenciado e versao confirmada
- [ ] Problema, escopo, metricas, restricoes, dependencias e riscos estao
      preenchidos de forma verificavel
- [ ] `Especificacao Funcional` e `Plano Tecnico` estao separados com
      precedencia explicita
- [ ] `Hipoteses Congeladas` registra lacunas resolvidas, hipoteses aceitas,
      dependencias pendentes e riscos de interpretacao
- [ ] Arquitetura geral e rollout estao descritos sem virar backlog
- [ ] Nao ha IDs `FEATURE-*`, IDs `US-*`, tabelas de backlog ou criterios de
      aceite por feature no PRD
- [ ] Proxima etapa explicita: `PROMPT-PRD-PARA-FEATURES.md`

## Relacao com os docs nucleares

| Documento | Papel |
|-----------|-------|
| `TEMPLATE-PRD.md` | estrutura e frontmatter do PRD |
| `PROMPT-INTAKE-PARA-PRD.md` | geracao do PRD a partir do intake |
| `PROMPT-PRD-PARA-FEATURES.md` | contrato operacional da etapa `PRD -> Features` |
| `GOV-FEATURE.md` | contrato do manifesto `FEATURE-*.md` |
| `TEMPLATE-FEATURE.md` | alvo de renderizacao do manifesto de feature |
| `SPEC-LEITURA-MINIMA-EVIDENCIA.md` | politica de leitura lean por evidencia |
