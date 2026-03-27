---
doc_id: "RELATORIO-AUDITORIA-MIGRATION-R01.md"
version: "1.0"
status: "done"
verdict: "hold"
feature_id: "OPENCLAW-MIGRATION"
reviewer_model: "GPT-5 Codex"
base_commit: "6e678617f41e"
round: 1
supersedes: "none"
followup_destination: "issue-local"
last_updated: "2026-03-25"
---

# RELATORIO-AUDITORIA - OPENCLAW-MIGRATION / FEATURE OPENCLAW-MIGRATION / R01

## Resumo Executivo

A implementacao da migracao entregou partes relevantes da governanca e dos templates, mas nao concluiu o eixo operacional exigido pelo PRD. O blocker dominante e `PROJETOS/COMUM/boot-prompt.md`, que permaneceu no fluxo `Fase > Epico > Issue` e inviabiliza a operacao autonoma na hierarquia nova. O veredito proposto e `hold`, com 0 de 3 Features completas e follow-ups bloqueantes locais.

## Escopo Auditado

- spec_path: `PROJETOS/OPENCLAW-MIGRATION/openclaw-migration-spec.md`
- audit_log: `PROJETOS/OPENCLAW-MIGRATION/AUDIT-LOG.md`
- base_commit: `6e678617f41e`
- target_commit: `2b8c914a696147cdcb04eaf4f6a2bb81609a1b81`
- diff/commit: `git diff 6e678617f41e..2b8c914`
- testes: nao aplicavel; auditoria documental dos artefatos `GOV-*`, `TEMPLATE-*`, `SESSION-*`, `boot-prompt.md` e skills listados no PRD
- drift_indice: `nenhuma` no sync inicial (`last_sync_at=2026-03-25T11:48:24+00:00`)
- evidencias_relevantes:
  - leitura integral dos artefatos das Features 1, 2 e 3 descritos no PRD
  - verificação de existencia/ausencia em `PROJETOS/COMUM/`
  - rastreio de termos legados por `rg`
  - confronto dos `passos_atomicos` com o diff `6e678617f41e..2b8c914`
  - verificação da superficie operacional ativa em `SESSION-MAPA.md` e prompts legados

## Conformidades

- `PROJETOS/COMUM/GOV-USER-STORY.md` foi criado com frontmatter completo e limites numericos explicitos (`max_tasks_por_user_story: 5`, `max_story_points_por_user_story: 5`).
- `PROJETOS/COMUM/TEMPLATE-AUDITORIA-FEATURE.md` e `PROJETOS/COMUM/TEMPLATE-ENCERRAMENTO.md` foram criados com frontmatter valido e estrutura coerente com o objetivo das User Stories 2.3 e 2.4.
- `.codex/skills/openclaw-autonomous/SKILL.md` e `.codex/skills/openclaw-router/SKILL.md` foram atualizadas para a nomenclatura `Feature` / `User Story`.
- `PROJETOS/COMUM/TEMPLATE-TASK.md` preservou os campos TDD `tdd_aplicavel`, `testes_red` e `passos_atomicos` sem regressao.

### VERIFICACAO - Feature 1: Documentos de Governanca Centrais

```text
VERIFICACAO - Feature 1: Documentos de Governanca Centrais
─────────────────────────────────────────
Artefatos esperados: 3
Artefatos encontrados: 3
Artefatos ausentes: nenhum

Por artefato:
| Arquivo | Existe? | Frontmatter ok? | Critérios atendidos? | Termos legados? |
|---------|---------|-----------------|----------------------|-----------------|
| PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md | sim | sim | parcial | sim |
| PROJETOS/COMUM/GOV-SCRUM.md | sim | sim | parcial | sim |
| PROJETOS/COMUM/GOV-USER-STORY.md | sim | sim | sim | nao |

Status da Feature: PARCIAL
─────────────────────────────────────────
```

### VERIFICACAO - Feature 2: Templates de Artefato

```text
VERIFICACAO - Feature 2: Templates de Artefato
─────────────────────────────────────────
Artefatos esperados: 4
Artefatos encontrados: 3
Artefatos ausentes: PROJETOS/COMUM/TEMPLATE-USER-STORY.md

Por artefato:
| Arquivo | Existe? | Frontmatter ok? | Critérios atendidos? | Termos legados? |
|---------|---------|-----------------|----------------------|-----------------|
| PROJETOS/COMUM/TEMPLATE-PRD.md | sim | sim | sim | nao |
| PROJETOS/COMUM/TEMPLATE-USER-STORY.md | nao | nao | nao | n-a |
| PROJETOS/COMUM/TEMPLATE-AUDITORIA-FEATURE.md | sim | sim | sim | sim |
| PROJETOS/COMUM/TEMPLATE-ENCERRAMENTO.md | sim | sim | sim | nao |

Status da Feature: PARCIAL
─────────────────────────────────────────
```

### VERIFICACAO - Feature 3: Documentos Operacionais e Skills

```text
VERIFICACAO - Feature 3: Documentos Operacionais e Skills
─────────────────────────────────────────
Artefatos esperados: 6
Artefatos encontrados: 6
Artefatos ausentes: nenhum

Por artefato:
| Arquivo | Existe? | Frontmatter ok? | Critérios atendidos? | Termos legados? |
|---------|---------|-----------------|----------------------|-----------------|
| PROJETOS/COMUM/boot-prompt.md | sim | n-a | nao | sim |
| PROJETOS/COMUM/SESSION-IMPLEMENTAR-US.md | sim | sim | parcial | nao |
| PROJETOS/COMUM/SESSION-AUDITAR-FEATURE.md | sim | sim | parcial | sim |
| PROJETOS/COMUM/SESSION-MAPA.md | sim | sim | parcial | nao |
| .codex/skills/openclaw-autonomous/SKILL.md | sim | sim | sim | nao |
| .codex/skills/openclaw-router/SKILL.md | sim | sim | sim | sim |

Status da Feature: PARCIAL
─────────────────────────────────────────
```

## Nao Conformidades

### VERIFICACAO DE CONSISTENCIA CRUZADA

| Item | Resultado | Evidencia |
|---|---|---|
| `GOV-FRAMEWORK-MASTER.md` referencia `GOV-USER-STORY.md` | sim | tabela de fontes de verdade, linha 69 |
| `GOV-FRAMEWORK-MASTER.md` referencia `TEMPLATE-AUDITORIA-FEATURE.md` | conflito PRD/prompt | o PRD manda apontar para `GOV-AUDITORIA-FEATURE.md`; o arquivo referencia `GOV-AUDITORIA-FEATURE.md` nas linhas 69-70 |
| `GOV-SCRUM.md` usa a cadeia `Intake > PRD > Features > User Stories > Tasks` sem termos legados fora de compatibilidade deprecated | nao | cadeia principal correta, mas linhas 34-35, 142-147 e 209-210 mantem `issue`/`SESSION-REVISAR-ISSUE.md` sem secao `deprecated` |
| `boot-prompt.md` usa Feature/US/Task nos niveis 4, 5 e 6 | nao | linhas 113-203 continuam em `Fases`, `Epicos`, `Issues` |
| `SESSION-MAPA.md` lista `SESSION-IMPLEMENTAR-US` e `SESSION-AUDITAR-FEATURE` e nao lista versoes depreciadas como ativas | nao | linhas 58-75 listam `SESSION-REVISAR-US.md` inexistente como `active`; prompts legados permanecem `status: active` nos arquivos antigos |
| `SESSION-IMPLEMENTAR-US.md` referencia `GOV-USER-STORY.md` como fonte de limite de tamanho | nao | nao ha nenhuma ocorrencia de `GOV-USER-STORY` no arquivo; o prompt operacional fica sem ponteiro normativo explicito |
| `SESSION-AUDITAR-FEATURE.md` referencia `TEMPLATE-AUDITORIA-FEATURE.md` | sim | linhas 35-43 |
| `.codex/skills/openclaw-router/SKILL.md` tem rota para `SESSION-IMPLEMENTAR-US` e `SESSION-AUDITAR-FEATURE` | sim | linhas 38-48 |
| Documentos depreciados tem `status: deprecated` e ponteiro para o substituto | nao | `SESSION-IMPLEMENTAR-ISSUE.md`, `SESSION-AUDITAR-FASE.md` e `SESSION-REVISAR-ISSUE.md` seguem `status: active` |
| `GOV-USER-STORY.md` define `max_tasks_por_user_story` com valor numerico explicito | sim | bloco YAML em `Limites Canonicos` |
| `TEMPLATE-TASK.md` manteve `tdd_aplicavel`, `testes_red`, `passos_atomicos` sem regressao | sim | frontmatter e secoes ainda presentes no arquivo |

### ACHADOS

| ID | Feature | Artefato | Categoria | Severidade | Evidencia | Bloqueante? |
|---|---|---|---|---|---|---|
| A-01 | F3 | `PROJETOS/COMUM/boot-prompt.md` | bug | critical | Linhas 19-37, 49-63, 113-203 e 285-314 continuam em `Fases > Epicos > Issues`; alem disso, o diff `6e678617f41e..2b8c914` nao incluiu o arquivo, apesar da Task 3.1.1 exigir sua reescrita. | sim |
| A-02 | F2 | `PROJETOS/COMUM/TEMPLATE-USER-STORY.md` | scope-drift | high | O arquivo nao existe no snapshot auditado; a US 2.2 / Task 2.2.1 exigia criacao do template com frontmatter e campos canonicos da User Story. | sim |
| A-03 | F3 | `PROJETOS/COMUM/SESSION-MAPA.md` | architecture-drift | high | Linhas 58-75 anunciam `SESSION-REVISAR-US.md` como prompt `active`, mas o arquivo nao existe; em paralelo, `SESSION-IMPLEMENTAR-ISSUE.md`, `SESSION-AUDITAR-FASE.md` e `SESSION-REVISAR-ISSUE.md` permanecem com `status: active`, contrariando a regra de depreciacao do PRD. | sim |
| A-04 | F1 | `PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md` | scope-drift | high | Linhas 57-60 mantem `issue-first` como padrao do repositorio e ainda delegam "arquivamento de fase" a `GOV-SCRUM.md`, sem secao de compatibilidade `deprecated`. | sim |
| A-05 | F1 | `PROJETOS/COMUM/GOV-SCRUM.md` | scope-drift | high | Linhas 34-35 ainda falam em `review pos-issue`; linhas 142-147 mantem `issue` como unidade de `Task Instructions`; linhas 209-210 apontam para `SESSION-REVISAR-ISSUE.md`. O arquivo nao elimina os termos legados como o criterio da Feature 1 exige. | sim |
| A-06 | F3 | `PROJETOS/COMUM/SESSION-AUDITAR-FEATURE.md` | bug | high | O bloco de bloqueio por follow-up nas linhas 190-195 manda usar `SESSION-IMPLEMENTAR-ISSUE.md` e `SESSION-REVISAR-ISSUE.md`, reintroduzindo o fluxo antigo justamente no SESSION de auditoria da nova arquitetura. | sim |

Total bloqueantes (critical + high): 6
Total nao bloqueantes (medium + low): 0

### SCOPE-DRIFT: A-02

```text
SCOPE-DRIFT: A-02
─────────────────────────────────────────
Spec declarava:    "Criar arquivo com frontmatter: doc_id, version, status, owner, last_updated, task_instruction_mode, feature_id, decision_refs" e adicionar os campos obrigatorios da User Story.
Implementado:      O arquivo `PROJETOS/COMUM/TEMPLATE-USER-STORY.md` nao existe.
Tipo de desvio:    incompleto
Impacto em cadeia: `SESSION-PLANEJAR-PROJETO`, criacao de USs novas e rastreabilidade documental da Feature 2 ficam sem template canonico.
─────────────────────────────────────────
```

### SCOPE-DRIFT: A-04

```text
SCOPE-DRIFT: A-04
─────────────────────────────────────────
Spec declarava:    Remover linhas referentes a Sprint e Epico da tabela, reescrever artefatos canonicos para `Feature > User Story > Task` e nao deixar "Sprint", "Epico" ou "Fase" fora de compatibilidade retroativa.
Implementado:      `GOV-FRAMEWORK-MASTER.md` atualizou a estrutura e as fontes principais, mas ainda preserva `issue-first` e "arquivamento de fase" nas linhas 57-60 sem marcacao `deprecated`.
Tipo de desvio:    incompleto
Impacto em cadeia: o documento-mestre continua descrevendo um repositorio parcialmente legado e contamina a leitura dos agentes que usam o master como mapa de alto nivel.
─────────────────────────────────────────
```

### SCOPE-DRIFT: A-05

```text
SCOPE-DRIFT: A-05
─────────────────────────────────────────
Spec declarava:    "Substituir 'Issue' por 'User Story' em toda a secao de Review-Ready", "Atualizar cascata de fechamento para: US > Feature" e remover referencias remanescentes a Sprint/Epico/Fase do ciclo operacional.
Implementado:      `GOV-SCRUM.md` atualizou a cadeia principal e parte da DoD, mas manteve `review pos-issue`, `issue` nas `Task Instructions` e `SESSION-REVISAR-ISSUE.md` como entrypoint de review.
Tipo de desvio:    incompleto
Impacto em cadeia: `GOV-SCRUM.md` continua instruindo agentes a operar no vocabulário antigo e quebra a consistencia com `SESSION-IMPLEMENTAR-US.md` e `SESSION-MAPA.md`.
─────────────────────────────────────────
```

## Analise Estrutural

| ID | Componente | Tipo | Linguagem | Metricas observadas | Threshold de referencia | Tendencia vs rodada anterior | Bloqueante? | Destino sugerido |
|---|---|---|---|---|---|---|---|---|
| M-01 | Artefatos Markdown da migracao | monolithic-file | Markdown | Nao aplicavel; a rodada auditou governanca documental, sem codigo executavel novo para medir contra `SPEC-ANTI-MONOLITO.md` | `SPEC-ANTI-MONOLITO.md` | nao aplicavel | nao | nenhum |

## Decisao

```text
VEREDITO PROPOSTO
─────────────────────────────────────────
veredito:                hold
features_completas:      0 de 3
bloqueantes_abertos:     6
nao_bloqueantes_abertos: 0
follow_up_destino:       issue-local

Justificativa:
O range auditado atualizou parte da governanca e dos templates, mas nao entregou
o eixo operacional minimo exigido pelo PRD. `boot-prompt.md` permaneceu na
arquitetura `issue-first`, `TEMPLATE-USER-STORY.md` nao foi criado e a
superficie `SESSION-*` ficou inconsistente entre rotas novas e legadas ativas.
Sem corrigir esses blockers, a migracao nao e executavel nem auditavel como
arquitetura Feature > User Story > Task.
─────────────────────────────────────────
```

- veredito: `hold`
- justificativa: ver bloco acima
- gate_da_feature: `hold`
- follow_up_destino_padrao: `issue-local`

## Follow-ups

### Follow-ups Bloqueantes

1. B1 — Criar `PROJETOS/COMUM/TEMPLATE-USER-STORY.md` com o frontmatter e os campos obrigatorios declarados na US 2.2, alinhado a `GOV-USER-STORY.md`.
2. B2 — Reescrever `PROJETOS/COMUM/boot-prompt.md` para que os Niveis 4, 5 e 6 operem em `Feature -> User Story -> Task`, incluindo quadro de confirmacao e fluxos de auditoria/fechamento coerentes.
3. B3 — Criar `PROJETOS/COMUM/SESSION-REVISAR-US.md`, corrigir `SESSION-MAPA.md`, `SESSION-AUDITAR-FEATURE.md` e `GOV-SCRUM.md`, e marcar `SESSION-IMPLEMENTAR-ISSUE.md`, `SESSION-AUDITAR-FASE.md` e `SESSION-REVISAR-ISSUE.md` como `status: deprecated` com ponteiro para os substitutos.
4. B4 — Limpar `PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md` de `issue-first` e outras referencias a `fase` fora de contexto explicitamente deprecated.

### Follow-ups Nao Bloqueantes

1. nenhum

AUDITORIA CONCLUIDA - VEREDITO: hold
─────────────────────────────────────────
Follow-ups bloqueantes: 4
Follow-ups nao bloqueantes: 0
─────────────────────────────────────────
Proximo passo: usar `SESSION-REMEDIAR-HOLD.md` ou uma US corretiva equivalente
para transformar os follow-ups acima em artefatos executaveis.

RELATORIO_PATH: `PROJETOS/OPENCLAW-MIGRATION/auditorias/RELATORIO-AUDITORIA-MIGRATION-R01.md`
AUDIT_LOG_PATH: `PROJETOS/OPENCLAW-MIGRATION/AUDIT-LOG.md`
─────────────────────────────────────────
