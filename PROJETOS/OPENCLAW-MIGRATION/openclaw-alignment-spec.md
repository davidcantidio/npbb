---
doc_id: "OPENCLAW-ALIGNMENT-SPEC"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-25"
---

# SPEC — Canonizacao End-to-End do OpenClaw para Paradigma Feature > User Story > Task

> Rastreabilidade canonica: esta spec e derivada de
> [PRD-OPENCLAW-MIGRATION.md](./PRD-OPENCLAW-MIGRATION.md).
> Ela existe para execucao e remediacao, nao como substituto do PRD.

---

## Intake

**Problema:** O repositorio ja possui governanca, skills, sessions e indice
SQLite parcialmente migrados para o paradigma `Feature -> User Story -> Task`,
mas o bootstrap real do framework ainda nasce no modelo antigo. Hoje,
`scripts/criar_projeto.py`, `bin/check-openclaw-smoke.sh`,
`PROJETOS/OC-SMOKE-SKILLS/` e parte da toolchain de metadata ainda operam em
`Fase -> Epico -> Issue -> Sprint`, o que quebra o alinhamento end-to-end.

**Oportunidade:** Consolidar o framework em um unico paradigma canonico,
fazendo com que:

- novos projetos nascam diretamente na arvore `features/.../user-stories/...`
- o indice SQLite v4 seja populado estruturalmente por projetos reais
- o smoke test valide o fluxo canonico de verdade
- skills, sessions, review, auditoria e hold remediation operem sobre o mesmo
  contrato sem adaptacao heuristica

**Criterio de sucesso:** Um projeto criado pelo framework deve:

- nascer com `Feature -> User Story -> Task`
- ser elegivel para o `boot-prompt.md`
- popular `features`, `user_stories`, `tasks` e `feature_audits` no SQLite v4
- passar no smoke local e remoto sem depender de `Fase`, `Epico`, `Issue` ou
  `Sprint`

---

## PRD

### Hierarquia canonica obrigatoria

```text
Intake -> PRD -> Feature -> User Story -> Task -> Review -> Feature Audit -> Hold Remediation -> Project Closing
```

### Invariantes

- Markdown continua sendo a fonte de verdade
- SQLite continua sendo indice derivado
- gate humano apenas em Intake e PRD
- gate senior em planejamento, review, auditoria e remediacao
- `GOV-COMMIT-POR-TASK.md` continua obrigatorio
- `SPEC-ANTI-MONOLITO.md` continua sendo a fonte de thresholds estruturais
- compatibilidade legada so pode existir em leitura, logs antigos ou secao
  explicitamente marcada como compatibilidade

### Regras inegociaveis

- nao criar novos artefatos `ISSUE-*`, `EPIC-*`, `SPRINT-*` ou `F*-*` como
  superficie principal
- nao manter scaffold hibrido em projetos novos
- `scripts/criar_projeto.py` deve gerar projeto consumivel por
  `boot-prompt.md`, `SESSION-*` canonicos e indice v4 sem adaptacao manual
- `bin/check-openclaw-smoke.sh` deve validar o fluxo canonico real, nao o
  legado
- `agents/openai.yaml` visiveis devem permanecer canonicos
- toda mudanca deve ser coberta por teste automatizado

### Dependencias entre Features

```text
Feature 1 -> sem dependencias
Feature 2 -> depende_de: [Feature 1]
Feature 3 -> depende_de: [Feature 1]
Feature 4 -> depende_de: [Feature 1, Feature 2]
Feature 5 -> depende_de: [Feature 1, Feature 2, Feature 3, Feature 4]
```

---

## Feature 1 — Scaffold Canonico de Projeto

**Objetivo:** Fazer `scripts/criar_projeto.py` gerar projetos inteiramente no
paradigma `Feature -> User Story -> Task`.

**Criterios de aceite:**
- projeto novo nasce com `features/FEATURE-1-FOUNDATION/...`
- wrappers locais apontam para `SESSION-IMPLEMENTAR-US`,
  `SESSION-REVISAR-US`, `SESSION-AUDITAR-FEATURE`
- nenhum projeto novo aponta para `SESSION-IMPLEMENTAR-ISSUE`,
  `SESSION-REVISAR-ISSUE` ou `SESSION-AUDITAR-FASE`

### User Story 1.1 — Migrar `scripts/criar_projeto.py`

**Como** mantenedor do framework,
**quero** que o script de bootstrap gere a arvore canonica do projeto,
**para** que todo projeto novo ja nasca compativel com o fluxo atual.

**Arquivos a tocar:**
- `scripts/criar_projeto.py`
- `tests/test_criar_projeto.py`

**Criterios Given/When/Then:**
- Given um repositorio sem projeto alvo
- When o agente roda `scripts/criar_projeto.py <PROJETO>`
- Then a pasta criada deve conter `features/FEATURE-1-FOUNDATION/`
- And a user story bootstrap deve existir em
  `user-stories/US-1-01-BOOTSTRAP/README.md`
- And a primeira task deve existir como `TASK-1.md`
- And nao deve haver `F1-FUNDACAO/`, `issues/` ou `sprints/`

**Tasks:**

#### Task 1.1.1
```yaml
objetivo: Substituir constantes e caminhos bootstrap legados por caminhos canonicos
tdd_aplicavel: false
arquivos_a_tocar:
  - scripts/criar_projeto.py
passos_atomicos:
  - Localizar constantes bootstrap baseadas em F1, EPIC, ISSUE e SPRINT
  - Substituir por constantes canonicas FEATURE-1-FOUNDATION e US-1-01-BOOTSTRAP
  - Definir paths fisicos para features/, user-stories/, TASK-1.md e auditorias/
resultado_esperado: Estrutura base do scaffold modelada em Feature -> User Story -> Task
```

#### Task 1.1.2
```yaml
objetivo: Reescrever renderizadores dos wrappers locais do projeto
tdd_aplicavel: false
arquivos_a_tocar:
  - scripts/criar_projeto.py
passos_atomicos:
  - Remover wrappers locais SESSION-IMPLEMENTAR-ISSUE, SESSION-REVISAR-ISSUE e SESSION-AUDITAR-FASE
  - Gerar wrappers locais SESSION-IMPLEMENTAR-US, SESSION-REVISAR-US e SESSION-AUDITAR-FEATURE
  - Manter wrappers de intake, PRD, planejamento, remediar hold e refatorar monolito
resultado_esperado: Projeto novo aponta apenas para sessions canonicas
```

#### Task 1.1.3
```yaml
objetivo: Reescrever testes do scaffold para o formato canonico
tdd_aplicavel: false
arquivos_a_tocar:
  - tests/test_criar_projeto.py
passos_atomicos:
  - Remover asserts baseados em F1-FUNDACAO, EPIC, ISSUE e SPRINT
  - Adicionar asserts para features/FEATURE-1-FOUNDATION
  - Adicionar asserts para user-stories/US-1-01-BOOTSTRAP/README.md e TASK-1.md
  - Adicionar assert de ausencia de arvore legacy no projeto novo
resultado_esperado: Testes validam exclusivamente o scaffold canonico
```

---

## Feature 2 — Smoke Test e Projeto de Referencia Canonicos

**Objetivo:** Fazer o smoke real do framework validar o paradigma novo.

**Criterios de aceite:**
- `bin/check-openclaw-smoke.sh` valida apenas artefatos canonicos
- `PROJETOS/OC-SMOKE-SKILLS/` representa um projeto smoke canonicamente migrado
- `GUIA-TESTE-SKILLS.md` descreve fluxos `User Story`, review e feature audit

### User Story 2.1 — Reescrever o smoke test

**Como** mantenedor do runtime,
**quero** que o smoke valide o fluxo correto,
**para** que um resultado verde signifique aderencia ao paradigma novo.

**Arquivos a tocar:**
- `bin/check-openclaw-smoke.sh`
- `PROJETOS/OC-SMOKE-SKILLS/GUIA-TESTE-SKILLS.md`

**Tasks:**

#### Task 2.1.1
```yaml
objetivo: Atualizar arquivos e prompts validados pelo smoke
tdd_aplicavel: false
arquivos_a_tocar:
  - bin/check-openclaw-smoke.sh
passos_atomicos:
  - Substituir referencias a SESSION-IMPLEMENTAR-ISSUE por SESSION-IMPLEMENTAR-US
  - Substituir referencias a SESSION-REVISAR-ISSUE por SESSION-REVISAR-US
  - Substituir referencias a SESSION-AUDITAR-FASE por SESSION-AUDITAR-FEATURE
  - Substituir validacao de paths F1-FUNDACAO/issues por paths sob features/.../user-stories/...
resultado_esperado: Smoke local valida o scaffold canonico
```

#### Task 2.1.2
```yaml
objetivo: Validar o DB v4 no smoke remoto
tdd_aplicavel: false
arquivos_a_tocar:
  - bin/check-openclaw-smoke.sh
passos_atomicos:
  - Adicionar query minima para COUNT(features), COUNT(user_stories) e COUNT(tasks)
  - Falhar se o projeto smoke nao popular as tabelas estruturadas
  - Manter verificacao de sync_meta.last_sync_at e sync_meta.repo_root
resultado_esperado: Smoke remoto prova populacao estrutural real do indice v4
```

#### Task 2.1.3
```yaml
objetivo: Reescrever o guia de smoke para o fluxo canonico
tdd_aplicavel: false
arquivos_a_tocar:
  - PROJETOS/OC-SMOKE-SKILLS/GUIA-TESTE-SKILLS.md
passos_atomicos:
  - Remover narrativa baseada em Fase, Issue e Sprint
  - Reescrever prompts de teste para Feature, User Story, review e auditoria
  - Alinhar o guia aos caminhos reais validados pelo smoke
resultado_esperado: Guia de smoke descreve apenas o paradigma novo
```

### User Story 2.2 — Migrar `OC-SMOKE-SKILLS` para a arvore canonica

**Arquivos a tocar:**
- `PROJETOS/OC-SMOKE-SKILLS/**`

**Tasks:**

#### Task 2.2.1
```yaml
objetivo: Converter o projeto smoke para Feature -> User Story -> Task
tdd_aplicavel: false
arquivos_a_tocar:
  - PROJETOS/OC-SMOKE-SKILLS/**
passos_atomicos:
  - Migrar a arvore estrutural de F1-FUNDACAO para features/FEATURE-1-FOUNDATION
  - Migrar issue bootstrap para user story bootstrap com README.md e TASK-1.md
  - Ajustar wrappers locais e audit-log do projeto smoke
resultado_esperado: Projeto smoke e elegivel para o boot-prompt canonico
```

---

## Feature 3 — Fluxo Completo de Execucao, Review, Auditoria e Remediacao

**Objetivo:** Consolidar a inteligencia operacional completa no novo paradigma.

**Criterios de aceite:**
- execucao termina em `ready_for_review`
- review reabre a mesma user story quando a correcao ainda pertence ao escopo original
- auditoria opera por feature
- hold remediation roteia deterministicamente para `same-feature`, `new-intake` ou `cancelled`

### User Story 3.1 — Blindar a execucao canonica

**Arquivos a tocar:**
- `PROJETOS/COMUM/SESSION-IMPLEMENTAR-US.md`
- `.codex/skills/openclaw-session-issue-execution/SKILL.md`

**Tasks:**

#### Task 3.1.1
```yaml
objetivo: Garantir determinismo de selecao de task e round
tdd_aplicavel: false
arquivos_a_tocar:
  - PROJETOS/COMUM/SESSION-IMPLEMENTAR-US.md
  - .codex/skills/openclaw-session-issue-execution/SKILL.md
passos_atomicos:
  - Confirmar precedencia active antes de todo na selecao de TASK-N.md
  - Confirmar round omitido ou 1 na primeira execucao
  - Confirmar round N+1 em retomada apos correcao_requerida
resultado_esperado: Execucao de US e deterministicamente reentrante
```

### User Story 3.2 — Blindar a revisao canonica

**Arquivos a tocar:**
- `PROJETOS/COMUM/SESSION-REVISAR-US.md`
- `.codex/skills/openclaw-session-issue-review/SKILL.md`

**Tasks:**

#### Task 3.2.1
```yaml
objetivo: Garantir persistencia na mesma user story antes da cascata documental
tdd_aplicavel: false
arquivos_a_tocar:
  - PROJETOS/COMUM/SESSION-REVISAR-US.md
  - .codex/skills/openclaw-session-issue-review/SKILL.md
passos_atomicos:
  - Confirmar regra de delta em README.md e TASK-N.md antes de ready_for_review -> active
  - Confirmar precedencia fechada de REVIEW_MODE
  - Confirmar tratamento explicito de SCOPE-LEARN.md
resultado_esperado: Review reabre a mesma US corretamente e sem backlog paralelo indevido
```

### User Story 3.3 — Blindar auditoria e remediacao de feature

**Arquivos a tocar:**
- `PROJETOS/COMUM/SESSION-AUDITAR-FEATURE.md`
- `PROJETOS/COMUM/SESSION-REMEDIAR-HOLD.md`
- `.codex/skills/openclaw-session-phase-audit/SKILL.md`
- `.codex/skills/openclaw-session-hold-remediation/SKILL.md`

**Tasks:**

#### Task 3.3.1
```yaml
objetivo: Garantir pre-checagem, hold remediation e compatibilidade residual controlada
tdd_aplicavel: false
arquivos_a_tocar:
  - PROJETOS/COMUM/SESSION-AUDITAR-FEATURE.md
  - PROJETOS/COMUM/SESSION-REMEDIAR-HOLD.md
  - .codex/skills/openclaw-session-phase-audit/SKILL.md
  - .codex/skills/openclaw-session-hold-remediation/SKILL.md
passos_atomicos:
  - Confirmar pre-checagem por User Stories e follow-ups bloqueantes
  - Confirmar uso operacional de same-feature como destino canonico
  - Manter issue-local apenas como compatibilidade residual de log
resultado_esperado: Auditoria e remedicao funcionam no paradigma novo sem ambiguidade
```

---

## Feature 4 — Banco de Dados Estruturado com Projetos Reais

**Objetivo:** Garantir que o indice v4 funcione com projetos reais criados pelo framework.

**Criterios de aceite:**
- projeto criado pelo scaffold popula `features`, `user_stories`, `tasks` e `feature_audits`
- projetos legados continuam apenas em `documents`
- smoke e testes consultam o DB estruturado corretamente

### User Story 4.1 — Validar ingestao estruturada real

**Arquivos a tocar:**
- `tests/test_openclaw_projects_index.py`

**Tasks:**

#### Task 4.1.1
```yaml
objetivo: Cobrir em teste o fluxo scaffold -> sync -> consulta SQL
tdd_aplicavel: false
arquivos_a_tocar:
  - tests/test_openclaw_projects_index.py
passos_atomicos:
  - Criar fixture via scripts/criar_projeto.py no formato canonico
  - Rodar sync do indice nessa fixture
  - Verificar COUNT(features)=1, COUNT(user_stories)>=1 e COUNT(tasks)>=1
  - Verificar que projeto legado continua apenas em documents quando presente
resultado_esperado: O indice v4 passa a ser validado com projetos reais do framework
```

---

## Feature 5 — Metadata Canonica das Skills e Toolchain de Deploy

**Objetivo:** Eliminar drift entre `SKILL.md`, `agents/openai.yaml`, scripts de validacao e deploy remoto.

**Criterios de aceite:**
- `validate_repo_skills` nao tenta reintroduzir nouns legados
- `agents/openai.yaml` visiveis nao usam `Issue`, `Phase`, `Epic` ou `Sprint`
- deploy para o sandbox nao provoca regressao semantica

### User Story 5.1 — Blindar metadata visivel

**Arquivos a tocar:**
- `bin/codex-skills-common.sh`
- `tests/test_openclaw_skill_scripts.py`
- `.codex/skills/*/agents/openai.yaml`

**Tasks:**

#### Task 5.1.1
```yaml
objetivo: Fixar labels e descricoes canonicas nas skills operacionais
tdd_aplicavel: false
arquivos_a_tocar:
  - bin/codex-skills-common.sh
  - tests/test_openclaw_skill_scripts.py
  - .codex/skills/openclaw-projects-index/agents/openai.yaml
  - .codex/skills/openclaw-session-project-planning/agents/openai.yaml
  - .codex/skills/openclaw-session-issue-execution/agents/openai.yaml
  - .codex/skills/openclaw-session-issue-review/agents/openai.yaml
  - .codex/skills/openclaw-session-phase-audit/agents/openai.yaml
passos_atomicos:
  - Garantir display_name canonico para execution, review, planning e audit
  - Garantir short_description coerente com User Story e Feature
  - Cobrir o contrato em teste automatizado
resultado_esperado: Validacao local e deploy remoto preservam labels canonicos
```

---

## Plano de Testes Obrigatorio

Executar no minimo:

```text
python3 -m pytest -q \
  tests/test_governance_docs.py \
  tests/test_review_same_issue_flow_docs.py \
  tests/test_openclaw_projects_index.py \
  tests/test_openclaw_skill_scripts.py \
  tests/test_criar_projeto.py
```

E tambem:

```text
./bin/check-openclaw-smoke.sh
./bin/check-openclaw-smoke.sh --remote --sandbox assis --gateway-name nemoclaw
./bin/sync-openclaw-projects-db.sh
```

Teste de integracao obrigatorio:

1. criar projeto temporario com `scripts/criar_projeto.py`
2. rodar sync do indice
3. verificar via SQL:
   - `COUNT(features)=1`
   - `COUNT(user_stories)>=1`
   - `COUNT(tasks)>=1`
4. confirmar que o projeto e elegivel para o `boot-prompt.md`

---

## Regras de Execucao deste Spec

1. Ler este arquivo inteiro antes de editar qualquer artefato
2. Executar as Features na ordem declarada
3. Dentro de cada Feature, executar User Stories na ordem listada
4. Dentro de cada User Story, executar Tasks na ordem numerada
5. Atualizar testes junto com a implementacao, nao depois
6. Nao declarar sucesso enquanto:
   - `scripts/criar_projeto.py` continuar gerando `F1-FUNDACAO/issues`
   - o smoke continuar validando `SESSION-IMPLEMENTAR-ISSUE`
   - o indice v4 continuar vazio em `features/user_stories/tasks` para projeto novo
7. Ao final, apresentar:
   - diff resumido
   - resultado dos testes
   - resultado do smoke local
   - resultado do smoke remoto
   - verificacao SQL do projeto criado pelo scaffold

---

## Saida Esperada Final

```text
VEREDITO FINAL
─────────────────────────────────────────
scaffold_canonico:        <ok | falhou>
smoke_canonico:          <ok | falhou>
skills_canonicas:        <ok | falhou>
review_audit_remediation:<ok | falhou>
sqlite_v4_estruturado:   <ok | falhou>
deploy_sandbox:          <ok | falhou>

Pendencias residuais:
- ...
─────────────────────────────────────────
```
