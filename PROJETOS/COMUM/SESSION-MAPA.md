---
doc_id: "SESSION-MAPA.md"
version: "3.0"
status: "active"
owner: "PM"
last_updated: "2026-03-26"
---

# SESSION-MAPA

> Mapa de todos os prompts de sessao disponiveis no framework.
> Use este arquivo como ponto de entrada quando operar em chat interativo
> em vez de Cloud Agent autonomo.
> O framework expoe **onze** prompts operacionais com nomenclatura canonica
> `SESSION-*.md` em estado `active` e **um** router legado de compatibilidade
> (`SESSION-PLANEJAR-PROJETO.md`) em estado `legacy_router`. Este ficheiro
> (`SESSION-MAPA.md`) e apenas o **mapa de entrada**: no diagrama em arvore
> serve para localizacao e **nao** entra na contagem dos doze prompts operacionais.
> A cadeia normativa completa e
> `Intake -> Clarificacao -> PRD -> Features -> User Stories -> Tasks -> Execucao -> Review -> Auditoria de Feature`.
> O PRD **nao** embute lista de Features nem User Stories (`GOV-PRD.md`); o desdobramento
> pos-PRD e etapa explicita (`SESSION-DECOMPOR-*` e `PROMPT-*-PARA-*`). A execucao segue a hierarquia entregavel
> `Feature -> User Story -> Task`.

## Indice operacional e memoria

- **Fonte de verdade:** Markdown em `PROJETOS/` versionado em Git.
- **Read model operacional:** Postgres (incl. `pgvector`), derivado por sync — contrato em
  `PROJETOS/COMUM/SPEC-INDICE-PROJETOS-POSTGRES.md`. Nao substitui edicao de artefatos nem gates
  normativos.

## Quando usar sessao de chat vs agente autonomo

| Situacao | Modo recomendado |
|---|---|
| quer acompanhamento passo a passo dos blocos operacionais | sessao de chat |
| tarefa bem definida, risco baixo, sem surpresas esperadas | `boot-prompt.md` |
| primeira vez executando uma feature, user story ou tipo de tarefa | sessao de chat |
| auditoria com achados potencialmente bloqueantes | sessao de chat |
| refatoracao de monolito | sessao de chat |
| execucao rotineira de user story em projeto maduro | `boot-prompt.md` |

## Modo OpenClaw Multi-Agente

- intake, clarificacao e PRD continuam com aprovacao humana explicita do usuario/PM
- apos o PRD aprovado, os gates de planejamento, review, auditoria e
  remediacao passam a ser exercidos obrigatoriamente pelo `agente senior`,
  sem checkpoints humanos intermediarios
- `agente senior` = modelo configurado em `OPENCLAW_AUDITOR_MODEL`, acessado
  via OpenRouter; o default operacional esperado e
  `openrouter/anthropic/claude-opus-4.6`
- o agente local implementa, testa e valida localmente ate
  `ready_for_review`
- `SESSION-*` continua sendo entrada interativa escolhida pelo humano, mas o
  operador apenas informa parametros e acompanha a trilha; nao aprova gates
  adicionais apos o PRD
- override humano apos o PRD so existe em conflitos de evidencia,
  cancelamento/aborto ou contexto externo novo explicitamente registrado
- quando a review ou auditoria exigirem correcao, o agente senior cria ou
  ajusta artefatos documentais dentro da user story/feature e o ciclo recomeca
- todo gate deve validar alinhamento explicito ao PRD (e aos manifestos de feature / US
  quando aplicavel) antes de aprovar

## Mapa de Prompts

```text
PROJETOS/COMUM/
  SESSION-CRIAR-INTAKE.md
  SESSION-CLARIFICAR-INTAKE.md
  SESSION-CRIAR-PRD.md
  SESSION-DECOMPOR-PRD-EM-FEATURES.md
  SESSION-DECOMPOR-FEATURE-EM-US.md
  SESSION-DECOMPOR-US-EM-TASKS.md
  SESSION-PLANEJAR-PROJETO.md  # router legado de compatibilidade
  SESSION-IMPLEMENTAR-US.md
  SESSION-IMPLEMENTAR-TASK.md
  SESSION-REVISAR-US.md
  SESSION-AUDITAR-FEATURE.md
  SESSION-REMEDIAR-HOLD.md
  SESSION-REFATORAR-MONOLITO.md
  SESSION-MAPA.md
```

## Prompts Disponiveis

| Prompt | Arquivo | Uso principal | Status |
|---|---|---|---|
| `SESSION-CRIAR-INTAKE` | `PROJETOS/COMUM/SESSION-CRIAR-INTAKE.md` | contexto bruto -> intake aprovado | active |
| `SESSION-CLARIFICAR-INTAKE` | `PROJETOS/COMUM/SESSION-CLARIFICAR-INTAKE.md` | intake aprovado -> bloco de clarificacao congelado para o PRD | active |
| `SESSION-CRIAR-PRD` | `PROJETOS/COMUM/SESSION-CRIAR-PRD.md` | intake aprovado -> PRD (para antes de Features; sem US/tasks no PRD) | active |
| `SESSION-DECOMPOR-PRD-EM-FEATURES` | `PROJETOS/COMUM/SESSION-DECOMPOR-PRD-EM-FEATURES.md` | PRD aprovado -> manifestos de feature (`PROMPT-PRD-PARA-FEATURES.md`) | active |
| `SESSION-DECOMPOR-FEATURE-EM-US` | `PROJETOS/COMUM/SESSION-DECOMPOR-FEATURE-EM-US.md` | Feature -> User Stories (`PROMPT-FEATURE-PARA-USER-STORIES.md`) | active |
| `SESSION-DECOMPOR-US-EM-TASKS` | `PROJETOS/COMUM/SESSION-DECOMPOR-US-EM-TASKS.md` | User Story -> Tasks (`PROMPT-US-PARA-TASKS.md`) | active |
| `SESSION-PLANEJAR-PROJETO` | `PROJETOS/COMUM/SESSION-PLANEJAR-PROJETO.md` | router legado de compatibilidade; preferir cadeia `SESSION-DECOMPOR-*` + prompts por etapa | legacy_router |
| `SESSION-IMPLEMENTAR-US` | `PROJETOS/COMUM/SESSION-IMPLEMENTAR-US.md` | execucao de user story especifica ate `ready_for_review` (fila de tasks na US) | active |
| `SESSION-IMPLEMENTAR-TASK` | `PROJETOS/COMUM/SESSION-IMPLEMENTAR-TASK.md` | execucao com entrada em `TASK-*.md`, leitura ascendente ate PRD/Intake, delega a `SESSION-IMPLEMENTAR-US` | active |
| `SESSION-REVISAR-US` | `PROJETOS/COMUM/SESSION-REVISAR-US.md` | gate do agente senior para `ready_for_review` e correcao iterativa da user story | active |
| `SESSION-AUDITAR-FEATURE` | `PROJETOS/COMUM/SESSION-AUDITAR-FEATURE.md` | gate senior de feature e follow-ups | active |
| `SESSION-REMEDIAR-HOLD` | `PROJETOS/COMUM/SESSION-REMEDIAR-HOLD.md` | relatorio hold -> user stories locais ou intakes de remediacao | active |
| `SESSION-REFATORAR-MONOLITO` | `PROJETOS/COMUM/SESSION-REFATORAR-MONOLITO.md` | intake de remediacao -> mini-projeto de decomposicao | active |

## Gatilhos Rapidos

| Necessidade | Prompt |
|---|---|
| gerar intake | `SESSION-CRIAR-INTAKE` |
| clarificar intake aprovado antes do PRD | `SESSION-CLARIFICAR-INTAKE` |
| gerar PRD | `SESSION-CRIAR-PRD` |
| PRD aprovado -> Features (manifestos) | `SESSION-DECOMPOR-PRD-EM-FEATURES` + `PROMPT-PRD-PARA-FEATURES` |
| Feature -> User Stories | `SESSION-DECOMPOR-FEATURE-EM-US` + `PROMPT-FEATURE-PARA-USER-STORIES` |
| User Story -> Tasks | `SESSION-DECOMPOR-US-EM-TASKS` + `PROMPT-US-PARA-TASKS` |
| compatibilidade com referencias historicas a planejamento monolitico | `SESSION-PLANEJAR-PROJETO` |
| executar uma user story (escolher proxima task na fila) | `SESSION-IMPLEMENTAR-US` |
| executar uma task conhecida (commit atomico, TDD por task) | `SESSION-IMPLEMENTAR-TASK` |
| fechar uma US `ready_for_review` ou revisar US ja executada | `SESSION-REVISAR-US` |
| auditar uma feature | `SESSION-AUDITAR-FEATURE` |
| rotear follow-ups de auditoria `hold` | `SESSION-REMEDIAR-HOLD` |
| transformar monolito em remediacao estruturada | `SESSION-REFATORAR-MONOLITO` |

## Relacao com o Boot Prompt

| Dimensao | `boot-prompt.md` | `SESSION-*.md` |
|---|---|---|
| entrada | agente autonomo recebe apenas o projeto | PM escolhe o prompt e informa os parametros |
| modo | autonomo | interativo |
| confirmacoes | nenhuma | humano apenas em intake/clarificacao/PRD; nenhum checkpoint humano apos PRD no fluxo feliz; override humano so em excecoes explicitas |
| descoberta de feature/user story/task | automatica no layout canonico (Markdown/Git + Postgres read model operacional derivado por sync) | sem descoberta autonoma; o PM informa feature, user story e task |
| escrita de arquivo | direta | sempre anunciada antes |
| ideal para | execucao repetitiva com proxima unidade inferida (US/Task) e auditorias quando elegiveis no boot | planejamento, execucao e revisao de US/Task (`SESSION-IMPLEMENTAR-TASK`, `SESSION-IMPLEMENTAR-US`, `SESSION-REVISAR-US`), auditoria de feature, remediacao hold, monolito e cenarios de alto risco |
