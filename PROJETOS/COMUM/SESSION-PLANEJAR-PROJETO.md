---
doc_id: "SESSION-PLANEJAR-PROJETO.md"
version: "4.0"
status: "legacy_router"
owner: "PM"
last_updated: "2026-03-25"
---

# SESSION-PLANEJAR-PROJETO — Router legado de planejamento pos-PRD

Este ficheiro **nao** e mais a sessao operacional monolitica de decomposicao.
Mantem-se como **roteador de compatibilidade**: aponta para etapas explicitas do
pipeline `PRD -> Features -> User Stories -> Tasks`, alinhadas ao contrato em que
o **PRD canônico nao lista Features nem User Stories** (ver `GOV-PRD.md` e
`TEMPLATE-PRD.md`).

Para trabalho novo, abra **directamente** a sessao especializada da etapa em
curso; use este router apenas quando um fluxo ou ferramenta ainda referenciar
`SESSION-PLANEJAR-PROJETO.md` pelo nome historico.

Os ficheiros `SESSION-DECOMPOR-*`, `PROMPT-PRD-PARA-FEATURES.md`,
`PROMPT-FEATURE-PARA-USER-STORIES.md`, `PROMPT-US-PARA-TASKS.md`, `GOV-PRD.md`,
`GOV-FEATURE.md` e `TEMPLATE-FEATURE.md` sao o **contrato canônico** publicado;
a tabela abaixo referencia esses caminhos.

## Sessoes canonicas (substituem o prompt unificado)

| Etapa do pipeline | Sessao | Prompt canonico associado |
|-------------------|--------|---------------------------|
| PRD (aprovado) -> Features | `PROJETOS/COMUM/SESSION-DECOMPOR-PRD-EM-FEATURES.md` | `PROJETOS/COMUM/PROMPT-PRD-PARA-FEATURES.md` |
| Feature -> User Stories | `PROJETOS/COMUM/SESSION-DECOMPOR-FEATURE-EM-US.md` | `PROJETOS/COMUM/PROMPT-FEATURE-PARA-USER-STORIES.md` |
| User Story -> Tasks | `PROJETOS/COMUM/SESSION-DECOMPOR-US-EM-TASKS.md` | `PROJETOS/COMUM/PROMPT-US-PARA-TASKS.md` |

Contratos documentais de apoio: `GOV-FEATURE.md`, `TEMPLATE-FEATURE.md`,
`GOV-USER-STORY.md`, `TEMPLATE-USER-STORY.md`, `SPEC-TASK-INSTRUCTIONS.md`,
`TEMPLATE-TASK.md`.

**Encerramento de projeto** (relatorio final): continue a usar
`TEMPLATE-ENCERRAMENTO.md` e as regras de auditoria de feature em
`GOV-FRAMEWORK-MASTER.md` / `SESSION-AUDITAR-FEATURE.md` — apenas depois de
cobertura e gates aplicaveis ao escopo.

## Parametros obrigatorios

Os parametros abaixo mantem-se **para alinhamento com skills e automatismos** que
ainda esperam este contrato. Preencha-os e encaminhe-os para a sessao escolhida na
tabela anterior (nao reproduza aqui o algoritmo monolitico antigo).

```text
PROJETO:       <nome do projeto, ex: FRAMEWORK-GOV>
PRD_PATH:      <caminho do PRD ou adendo aprovado do PRD, ex: PROJETOS/FRAMEWORK-GOV/PRD-FRAMEWORK-GOV.md>
ESCOPO:        <"projeto completo" | "apenas FEATURE-<N>-<NOME>" | "apenas US-<N>-<NN>-<NOME>" | "encerramento">
PROFUNDIDADE:  <"features" | "features+user_stories" | "completo" | "encerramento">
TASK_MODE:     <"optional" | "required" | "por user story">
OBSERVACOES:   <restricoes adicionais ou "nenhuma">
```

## Roteamento deterministico (mapa legado -> sessoes novas)

1. **Sempre** comece por confirmar `PRD_PATH` (PRD base ou adendo aprovado; se
   for adendo, leia o PRD base referenciado). Lacunas que impecam decomposicao
   sao tratadas na **sessao da etapa**, com `BLOQUEADO` quando o insumo daquela
   etapa for insuficiente — **nao** exija que o PRD liste Features ou User
   Stories.
2. `PROFUNDIDADE: features` ou primeiro passo de `features+user_stories` /
   `completo`: `SESSION-DECOMPOR-PRD-EM-FEATURES.md` + `PROMPT-PRD-PARA-FEATURES.md`.
3. `ESCOPO` recortando uma feature ou `PROFUNDIDADE` incluindo user stories:
   `SESSION-DECOMPOR-FEATURE-EM-US.md` + `PROMPT-FEATURE-PARA-USER-STORIES.md`
   (por feature aplicavel).
4. Detalhe de tasks (`completo`, ou `TASK_MODE` aplicavel): `SESSION-DECOMPOR-US-EM-TASKS.md`
   + `PROMPT-US-PARA-TASKS.md` (por user story aplicavel).
5. `PROFUNDIDADE: encerramento` ou `ESCOPO: encerramento`: relatorio de
   encerramento conforme `TEMPLATE-ENCERRAMENTO.md`; bloqueie se faltar auditoria
   final `go` onde a governanca exigir.

## Ordem de leitura transversal (ainda valida)

1. `PROJETOS/COMUM/boot-prompt.md` (niveis aplicaveis)
2. `PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md`
3. A sessao especializada escolhida e o prompt canonico da etapa
4. Artefactos do projeto: `{{PRD_PATH}}`, `PROJETOS/<PROJETO>/INTAKE-<PROJETO>.md`

## Pre-condicao operacional: indice derivado de `PROJETOS/`

Antes do primeiro gate de planejamento na etapa em curso, sincronize o indice
operacional conforme o processo canônico vigente em `GOV-FRAMEWORK-MASTER.md`
(por exemplo `./bin/sync-openclaw-projects-db.sh` enquanto o read model for
SQLite; após cutover, seguir `SPEC-INDICE-PROJETOS-POSTGRES.md`).

1. execute o sync canônico
2. consulte o estado do projeto e do escopo pedido no indice
3. compare com o Markdown em Git; o **Markdown prevalece**
4. registre `DRIFT_INDICE: <nenhuma | descricao>` antes do primeiro gate da etapa
5. após gravacoes em `PROJETOS/` que alterem features, user stories, tasks ou
   encerramento, execute novo sync

## Literais de bloco (referencia para etapas especializadas)

As sessoes novas reproduzem ou refinam estes literais; mantenha coerencia entre
etapas:

```text
DRIFT_INDICE: <nenhuma | descricao>
```

```text
[NIVEL CONCLUIDO: Features | User Stories | Tasks | Encerramento]
─────────────────────────────────────────
Total de itens: X | Alertas: Z
DRIFT_INDICE: <nenhuma | descricao>
Lacunas identificadas no insumo da etapa: <nenhuma | lista>
─────────────────────────────────────────
Resultado esperado do gate: `APROVADO | AJUSTAR | REPROVADO`
```

## Regra de compatibilidade

Quando documentacao de projeto, skills ou scripts ainda disserem "seguir
`SESSION-PLANEJAR-PROJETO`", interprete como: **aplicar este router e executar a
cadeia de sessoes especializadas** equivalente ao `ESCOPO` e `PROFUNDIDADE`
pedidos — sem reintroduzir PRD com listas de Features ou User Stories.
