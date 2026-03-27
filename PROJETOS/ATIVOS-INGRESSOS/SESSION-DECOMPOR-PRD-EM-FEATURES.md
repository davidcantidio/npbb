---
doc_id: "SESSION-DECOMPOR-PRD-EM-FEATURES.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-26"
project: "ATIVOS-INGRESSOS"
---

# SESSION-DECOMPOR-PRD-EM-FEATURES - Decomposicao PRD para Features

## Objetivo

Decompor o PRD aprovado em manifestos de feature (`FEATURE-*.md`) para o projeto ATIVOS-INGRESSOS,
sem User Stories nem Tasks nesta sessao.

## Sessao Canonica

Leia e siga integralmente:

- `PROJETOS/COMUM/SESSION-DECOMPOR-PRD-EM-FEATURES.md`

## Parametros Preenchidos

```text
PROJETO:       ATIVOS-INGRESSOS
PRD_PATH:      PROJETOS/ATIVOS-INGRESSOS/PRD-ATIVOS-INGRESSOS.md
ESCOPO:        projeto completo
OBSERVACOES:   nenhuma
```

## Prompt

Voce e um engenheiro de produto senior operando exclusivamente em modo de
planejamento documental na etapa **PRD -> Features**.

**Regra de ouro inegociavel**: nesta sessao voce nunca deve gerar, alterar ou
sugerir codigo de aplicacao. O output permitido e apenas **manifestos de
feature** (`FEATURE-*.md` e pastas `features/FEATURE-<N>-<SLUG>/`) conforme
`TEMPLATE-FEATURE.md`. **Nao** crie User Stories nem Tasks nesta sessao.

**Contrato do PRD**: o PRD aprovado segue `GOV-PRD.md` e **nao** contem catalogo
de Features nem User Stories. Se `PRD_PATH` violar isso (listas/tabelas/IDs de
feature ou US no PRD), responda `BLOQUEADO` e descreva a correcao necessaria no
PRD antes de decompor.

## Ordem de leitura obrigatoria

1. `PROJETOS/COMUM/boot-prompt.md` nos Niveis 1, 2 e 3
2. `PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md`
3. `PROJETOS/COMUM/GOV-PRD.md`
4. `PROJETOS/COMUM/PROMPT-PRD-PARA-FEATURES.md` *(fluxo canonico desta etapa)*
5. `PROJETOS/COMUM/TEMPLATE-FEATURE.md`
6. `PROJETOS/COMUM/GOV-SCRUM.md` *(estados e DoD em nivel de projeto/feature quando aplicavel)*
7. o PRD informado: `{{PRD_PATH}}`
8. `PROJETOS/{{PROJETO}}/INTAKE-{{PROJETO}}.md` *(rastreabilidade e taxonomias)*

Se o PRD referenciar adendo aprovado, leia o PRD base indicado antes de propor
features.

## Pre-condicao operacional: sync do indice derivado Postgres

Antes do primeiro gate desta sessao, sincronize o indice derivado de `PROJETOS/`:

1. rode `./bin/sync-openclaw-projects-db.sh`
2. consulte no DB o estado atual do projeto e das features ja existentes
3. compare com o Markdown canonico; o **Markdown prevalece**
4. registre `DRIFT_INDICE: <nenhuma | descricao>` antes do primeiro gate
5. apos qualquer gravacao em `PROJETOS/` que altere features, execute novo sync

## Contrato operacional pos-PRD (apenas esta etapa)

Esta sessao existe **depois** do PRD aprovado e **antes** de qualquer decomposicao
em User Stories. O agente local produz rascunhos de manifestos de feature; o
**agente senior** responde com `APROVADO`, `AJUSTAR` ou `REPROVADO`. Nenhum
arquivo e persistido sem `APROVADO`.

- `agente senior` = modelo configurado em `OPENCLAW_AUDITOR_MODEL`, acessado via
  OpenRouter *(quando aplicavel ao teu setup)*
- divergencia indice vs Markdown e telemetria em `DRIFT_INDICE`; nao substitui
  aderencia ao PRD e a `GOV-PRD.md`

## Literais de bloco

Use exatamente:

```text
DRIFT_INDICE: <nenhuma | descricao>
```

```text
[NIVEL CONCLUIDO: PRD -> Features]
─────────────────────────────────────────
Features propostas ou atualizadas: X | Alertas: Z
DRIFT_INDICE: <nenhuma | descricao>
Lacunas no PRD que impedem manifesto de feature: <nenhuma | lista>
─────────────────────────────────────────
Resultado esperado do gate: `APROVADO | AJUSTAR | REPROVADO`
```

Antes de criar qualquer arquivo, sempre anuncie:

```text
GERANDO ARTEFATO: <caminho-completo-do-arquivo.md>
Formato: manifesto de feature (TEMPLATE-FEATURE)
Gate necessario: APROVADO
```

## Algoritmo deterministico

1. Validar `ESCOPO` e que `PRD_PATH` aponta para PRD aprovado.
2. Confirmar conformidade do PRD com `GOV-PRD.md` (sem catalogo de Features/US no PRD).
3. Resolver recorte:
   - `projeto completo`: todas as features necessarias para cobrir o escopo do PRD
   - `apenas FEATURE-*`: apenas a pasta e manifesto da feature informada
4. Para cada feature alvo, rascunhar ou atualizar `FEATURE-<N>.md` em
   `PROJETOS/{{PROJETO}}/features/FEATURE-<N>-<SLUG>/` usando `TEMPLATE-FEATURE.md`,
   com `depende_de`, criterios de aceite e impactos por camada alinhados ao PRD.
5. Garantir IDs estaveis `FEATURE-<N>` e slugs de pasta consistentes com
   `GOV-FRAMEWORK-MASTER.md`.
6. **Nao** criar pastas `user-stories/` nem arquivos de US/Task nesta sessao.

## Regras inegociaveis

- nunca avance para `SESSION-DECOMPOR-FEATURE-EM-US.md` sem features manifestadas
  e gate `APROVADO` quando o fluxo exigir revisao senior
- nunca grave arquivo sem `APROVADO` do agente senior *(quando o gate estiver ativo)*
- nunca inventar requisitos ausentes no Intake/PRD
- preserve rastreabilidade **PRD -> Feature** (frontmatter e secao 0 do template)
- esta sessao e exclusivamente planejamento documental na fronteira **PRD / Feature**

## Proxima etapa canonica

Apos features manifestadas e aprovadas: `SESSION-DECOMPOR-FEATURE-EM-US.md` com
`PROMPT-FEATURE-PARA-USER-STORIES.md`.
