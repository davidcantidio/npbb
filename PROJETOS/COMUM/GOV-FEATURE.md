---
doc_id: "GOV-FEATURE.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-25"
---

# GOV-FEATURE

## Objetivo

Definir o **contrato normativo** do manifesto de **Feature** no OpenClaw: conteúdo
obrigatório, dependências entre features, limites em relação ao PRD e às User
Stories, e critérios para decompor a feature em User Stories.

A feature é artefato **documental versionado em Git** em
`features/FEATURE-<N>-<SLUG>/FEATURE-<N>.md`. Não substitui o PRD (estratégico)
nem detalha execução por task (isso fica nas US e em `TASK-*.md`).

## Fonte de verdade

- **Markdown + Git** são canónicos para criar, editar e aprovar manifestos de feature.
- Índices derivados (SQLite legado, Postgres read model) **espelham** paths e
  front matter; não são fonte de escrita do backlog.

## Cadeia no pipeline

```text
Intake -> PRD -> Features -> User Stories -> Tasks -> Execucao -> Review -> Auditoria de Feature
```

A etapa **PRD -> Features** usa `PROMPT-PRD-PARA-FEATURES.md` e
`SESSION-DECOMPOR-PRD-EM-FEATURES.md`. A feature existe **após** essa etapa, não
dentro do corpo do PRD (ver `GOV-PRD.md`).

## Regras canónicas

1. Cada feature ativa tem **um** manifesto `FEATURE-<N>.md` na pasta
   `PROJETOS/<PROJETO>/features/FEATURE-<N>-<SLUG>/`, alinhado a
   `GOV-FRAMEWORK-MASTER.md` e `TEMPLATE-FEATURE.md`.
2. O manifesto **deve** referenciar o PRD e o intake (caminhos relativos e/ou
   front matter `prd_path`, `intake_path`) para rastreabilidade **PRD -> Feature**.
3. O manifesto **consolida** comportamento entregável, critérios de aceite da
   feature, riscos específicos, impacto por camada e **dependências entre features**
   (`depende_de` no front matter e secção 3 do template).
4. O manifesto **não** substitui critérios Given/When/Then nem tarefas
   executáveis: isso vive em `user-stories/US-*/README.md` e `TASK-*.md`.
5. A secção **User Stories (rastreabilidade)** no template (tabela com links) é
   **índice de ligação** às US já criadas, não substitui a etapa
   **Feature -> User Stories** (`PROMPT-FEATURE-PARA-USER-STORIES.md`).
6. IDs estáveis: `FEATURE-<N>` e pastas `FEATURE-<N>-<SLUG>` devem permanecer
   coerentes; renomeações exigem atualização de referências e sync do índice.

## Dependências entre features

- Declare no front matter `depende_de` uma lista de `feature_key` (ex. `FEATURE-1`)
  ou caminhos relativos acordados ao projeto.
- Uma feature **não** deve ser considerada completa para auditoria enquanto
  dependências declaradas **bloqueantes** não estiverem satisfeitas (estados:
  `GOV-SCRUM.md`, `GOV-AUDITORIA-FEATURE.md`).
- Evite ciclos; se houver acoplamento real, documente ordem de entrega no PRD em
  nível de tema (sem lista de features no PRD) e reflete no `depende_de`.

## Critérios para decompor em User Stories

Antes de `SESSION-DECOMPOR-FEATURE-EM-US.md`:

- Critérios de aceite da feature são **verificáveis** e cobrem o comportamento
  prometido ao negócio.
- **Impactos por camada** estão preenchidos o suficiente para fatiar trabalho sem
  ambiguidade arquitetural grave.
- Cada User Story proposta deve:
  - caber nos limites de `GOV-USER-STORY.md` (story points, tasks por US quando
    aplicável ao planeamento);
  - mapear a pelo menos um critério de aceite da feature ou a um risco mitigado;
  - ter `feature_id` coerente com `FEATURE-<N>` no `README.md` da US.

Se o manifesto estiver incompleto, a resposta correta é `BLOQUEADO` com lacunas
objetivas (ver `SESSION-DECOMPOR-FEATURE-EM-US.md`).

## O que a feature não é

- Não é o PRD (sem repetir escopo global inteiro nem rollout completo do projeto).
- Não é lista de tasks (use `SESSION-DECOMPOR-US-EM-TASKS.md`).
- Não é relatório de auditoria (use `auditorias/RELATORIO-AUDITORIA-*.md`).

## Checklist de conformidade (manifesto)

- [ ] `feature_key`, pasta e `GOV-FRAMEWORK-MASTER` alinhados
- [ ] PRD e intake referenciados
- [ ] `depende_de` coerente com ordem de entrega
- [ ] Critérios de aceite e impactos por camada preenchidos
- [ ] Tabela de US atualizada após criar ou renomear US

## Relação com outros documentos

| Documento | Papel |
|-----------|--------|
| `GOV-PRD.md` | PRD sem catálogo de features/US |
| `TEMPLATE-FEATURE.md` | Estrutura do manifesto |
| `PROMPT-PRD-PARA-FEATURES.md` | Decomposição PRD -> manifestos |
| `SESSION-DECOMPOR-PRD-EM-FEATURES.md` | Sessão dessa etapa |
| `PROMPT-FEATURE-PARA-USER-STORIES.md` | Decomposição Feature -> US |
| `SESSION-DECOMPOR-FEATURE-EM-US.md` | Sessão dessa etapa |
| `GOV-USER-STORY.md` | Limites e elegibilidade da US |
| `GOV-SCRUM.md` | Estados e ciclo após existirem artefatos |
| `GOV-AUDITORIA-FEATURE.md` | Gate e auditoria de feature |

## Responsabilidade deste documento

- Fixar o contrato do manifesto de feature e a fronteira com PRD, US e tasks.
- Não duplicar DoD de US nem formato de task; remeter a `GOV-USER-STORY.md` e
  `SPEC-TASK-INSTRUCTIONS.md` quando necessário.
