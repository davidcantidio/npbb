---
doc_id: "GOV-PRD.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-25"
---

# GOV-PRD

## Objetivo

Definir o **contrato normativo** do Product Requirements Document (PRD) no OpenClaw:
o que o PRD deve descrever, o que fica **fora** do PRD, e como ele se encaixa na cadeia
`Intake -> PRD -> Features -> User Stories -> Tasks -> Execucao -> Review -> Auditoria de Feature`.

O PRD e artefato **estratégico e de produto**: problema, direcao, escopo, restricoes, riscos,
metricas, visao arquitetural geral e rollout. A **decomposicao entregavel** (features, user stories,
tasks) e etapa **posterior** e explicita do pipeline, nao conteudo do PRD.

## Fonte de verdade

- **Markdown versionado em Git** e a fonte canonica do PRD e dos demais artefatos de governanca.
- Indices operacionais (ex.: Postgres read model) podem **derivar** metadados do PRD; nao substituem o arquivo.

## Regras canonicas

1. Todo projeto ativo referencia um PRD principal `PRD-<PROJETO>.md` (ou variante com slug quando aplicavel),
   com rastreabilidade ao intake conforme `GOV-INTAKE.md`.
2. O PRD **nao** lista **Features** nem **User Stories** como secao de planejamento entregavel. Isso inclui
   tabelas, catalogos, IDs (`Feature N`, `US-x.y`) ou roadmaps fatiados nesse nivel.
3. O PRD **pode** mencionar, em linguagem de alto nivel, **capacidades** ou **temas** que o produto deve
   enderecar, desde que nao substituam manifestos de feature nem constituam backlog estruturado
   (sem IDs de feature, sem criterios de aceite por feature, sem tabelas de US no PRD).
4. A passagem de PRD para backlog estruturado de features ocorre apenas via etapa dedicada, usando
   `PROMPT-PRD-PARA-FEATURES.md` e `SESSION-DECOMPOR-PRD-EM-FEATURES.md` (prompt e sessao canonicos).
5. O conteudo obrigatorio do corpo do PRD segue a estrutura acordada em `TEMPLATE-PRD.md`, **apenas nas
   secoes que o template mantiver como escopo do PRD** (apos alinhamento do template ao presente contrato).

## Conteudo obrigatorio (contrato do PRD)

O PRD deve cobrir, de forma auditavel:

| Area | Expectativa |
|------|-------------|
| **Problema / oportunidade** | Contexto, evidencia, custo de nao agir, por que agora |
| **Objetivo e valor** | Resumo executivo, resultado de negocio esperado |
| **Publico e operadores** | Quem usa, quem opera, quem aprova ou patrocina |
| **Jobs to be done** | Trabalho que o usuario contrata o produto para fazer |
| **Escopo** | Dentro / fora, nao-objetivos |
| **Metricas** | Leading, lagging, criterio minimo de sucesso |
| **Restricoes e guardrails** | Tecnicas, operacionais, legais, prazo, marca/design |
| **Dependencias e integracoes** | Sistemas, dados de entrada/saida, impactos em alto nivel |
| **Arquitetura geral** | Visao unificada de backend, frontend, dados, observabilidade, auth quando relevante — **sem** substituir o detalhamento por feature em `FEATURE-*.md` |
| **Riscos globais** | Produto, tecnico, operacional, dados, adocao |
| **Rollout** | Estrategia de deploy, comunicacao, treinamento, suporte pos-launch |
| **Revisoes e auditorias** | Expectativa de gates e auditorias **em nivel de projeto** (referencias a `GOV-AUDITORIA.md`, thresholds), **sem** listar features ou US como itens de backlog no PRD |

Rastreabilidade no frontmatter e secao de rastreio (intake, versoes, taxonomias herdadas do intake)
permanecem obrigatorias conforme `GOV-INTAKE.md` e `TEMPLATE-PRD.md`.

## O que o PRD nao e

- Nao e backlog de **Features** (isso vive em `features/FEATURE-<N>-<NOME>/FEATURE-<N>.md` e em
  `GOV-FEATURE.md`).
- Nao e lista de **User Stories** nem de **Tasks** (isso vive sob cada feature e em `GOV-USER-STORY.md`,
  `GOV-SCRUM.md`).
- Nao substitui **manifesto de feature** nem **relatorio de auditoria de feature**; apenas contextualiza
  o projeto para essas etapas.

## Checklist de conformidade (PRD)

Antes de considerar o PRD pronto para a etapa `PRD -> Features`:

- [ ] Intake referenciado e versao confirmada
- [ ] Problema, escopo, restricoes, riscos e metricas estao preenchidos de forma verificavel
- [ ] Arquitetura geral e rollout estao descritos sem depender de lista de features no PRD
- [ ] **Nao** ha secao de catalogo de Features nem tabelas de User Stories planejadas no PRD
- [ ] Proxima etapa explicita: decomposicao via `SESSION-DECOMPOR-PRD-EM-FEATURES.md` / `PROMPT-PRD-PARA-FEATURES.md`

## Relacao com outros documentos

| Documento | Papel |
|-----------|--------|
| `GOV-INTAKE.md` | Gate e taxonomias `Intake -> PRD` |
| `TEMPLATE-PRD.md` | Estrutura e frontmatter do arquivo PRD |
| `PROMPT-INTAKE-PARA-PRD.md` | Geracao do PRD a partir do intake (ate o escopo do PRD) |
| `SESSION-CRIAR-PRD.md` | Sessao interativa de criacao do PRD |
| `GOV-FEATURE.md` | Contrato do manifesto de feature (downstream do PRD) |
| `GOV-SCRUM.md` | Ciclo Feature > US > Task apos existirem artefatos correspondentes |

## Responsabilidade deste documento

- Fixar o contrato do PRD **sem** Features/User Stories no corpo normativo.
- Evitar duplicar Definition of Done, estados de US ou regras de auditoria detalhadas; remeter a
  `GOV-SCRUM.md`, `GOV-USER-STORY.md` e `GOV-AUDITORIA.md` quando necessario.
