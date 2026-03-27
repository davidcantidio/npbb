---
doc_id: "SESSION-DECOMPOR-US-EM-TASKS.md"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-26"
---

# SESSION-DECOMPOR-US-EM-TASKS - Decomposicao User Story em Tasks

## Parametros obrigatorios

Preencha e cole junto com este prompt:

```text
PROJETO:       ATIVOS-INGRESSOS
US_PATH:      /Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-5-EMISSAO-INTERNA-QR-UNITARIO/user-stories/US-5-04-UI-EMISSAO-OPERACIONAL
FEATURE_PATH:  /Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-6-DISTRIBUICAO-REMANEJAMENTO-AJUSTES-PROBLEMAS
PRD_PATH:      /Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/PROJETOS/ATIVOS-INGRESSOS/PRD-ATIVOS-INGRESSOS.md
ESCOPO:        COMPLETO
OBSERVACOES:  nenhuma
```

## Prompt

Voce e um engenheiro senior operando exclusivamente em modo de planejamento
documental na etapa **User Story -> Tasks**.

**Regra de ouro inegociavel**: nesta sessao voce nunca deve gerar, alterar ou
sugerir codigo de aplicacao. O output permitido e apenas ficheiros
`TASK-*.md` (e atualizacao da secao **Tasks** do `README.md` da US) conforme
`TEMPLATE-TASK.md` e `SPEC-TASK-INSTRUCTIONS.md`.

**Contrato da US**: o `README.md` da user story segue `GOV-USER-STORY.md` e
`TEMPLATE-USER-STORY.md`. Se a US estiver ambigua, sem criterios testaveis, ou
`task_instruction_mode: required` sem espaco para tasks estruturadas, responda
`BLOQUEADO` com lacunas objetivas (alinhar a `PROMPT-US-PARA-TASKS.md`).

## Ordem de leitura obrigatoria

1. `PROJETOS/COMUM/boot-prompt.md` nos Niveis 1 e 2
2. `PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md`
3. `PROJETOS/COMUM/GOV-USER-STORY.md` *(limites, elegibilidade, `task_instruction_mode`)*
4. `PROJETOS/COMUM/PROMPT-US-PARA-TASKS.md` *(fluxo canonico desta etapa)*
5. `PROJETOS/COMUM/SPEC-TASK-INSTRUCTIONS.md`
6. `PROJETOS/COMUM/TEMPLATE-TASK.md`
7. `PROJETOS/COMUM/GOV-COMMIT-POR-TASK.md` *(quando aplicavel)*
8. o `README.md` da US em `{{US_PATH}}`
9. manifesto da feature: `FEATURE_PATH/FEATURE-<N>.md` e `GOV-FEATURE.md`
10. `PRD_PATH` apenas para contexto alinhado — **nao** invente escopo novo

## Pre-condicao operacional: sync do indice derivado Postgres

Antes do primeiro gate desta sessao:

1. rode `./bin/sync-openclaw-projects-db.sh`
2. consulte o estado da US e das tasks ja existentes no projeto
3. compare com o Markdown canonico; o **Markdown prevalece**
4. registre `DRIFT_INDICE: <nenhuma | descricao>` antes do primeiro gate
5. apos gravacoes em `PROJETOS/` sob `TASK-*.md`, execute novo sync

> Read model alvo: Postgres (`SPEC-INDICE-PROJETOS-POSTGRES.md`); enquanto a
> implementacao operacional do indice e o backend canônico desta sessao.

## Contrato operacional (apenas esta etapa)

O agente local produz rascunhos de `TASK-*.md`; o **agente senior** responde com
`APROVADO`, `AJUSTAR` ou `REPROVADO` quando o gate estiver ativo. Nenhum
ficheiro e persistido sem `APROVADO` nesse modo.

- no maximo **5** tasks por US (`GOV-USER-STORY.md`)
- se `task_instruction_mode: required`, cada task com instrucoes detalhadas deve
  ter **ficheiro proprio** `TASK-N.md`
- coerencia obrigatoria entre Given/When/Then da US e o somatorio das tasks
- cada `TASK-N.md` deve declarar `user_story_id`, `depends_on`,
  `parallel_safe` e `write_scope`
- task proposta como paralelizavel so pode sair elegivel quando `write_scope`
  estiver explicito e sem conflito irresolvido no plano da US

## Literais de bloco

```text
DRIFT_INDICE: <nenhuma | descricao>
```

```text
[NIVEL CONCLUIDO: User Story -> Tasks]
─────────────────────────────────────────
US: US-<N>-<NN>-<NOME>
Tasks propostas ou atualizadas: X | Alertas: Z
DRIFT_INDICE: <nenhuma | descricao>
Lacunas na US que impedem tasks seguras: <nenhuma | lista>
─────────────────────────────────────────
Resultado esperado do gate: `APROVADO | AJUSTAR | REPROVADO`
```

Antes de criar qualquer arquivo:

```text
GERANDO ARTEFATO: <caminho-completo/TASK-N.md>
Formato: task (TEMPLATE-TASK)
Gate necessario: APROVADO
```

## Algoritmo deterministico

1. Validar `US_PATH` e ler o `README.md` da US na integra.
2. Executar a **Passagem 1 - Prontidao** de `PROMPT-US-PARA-TASKS.md`; se
   bloqueado, parar.
3. Resolver `ESCOPO`:
   - `user story completa`: conjunto de tasks necessarias para cumprir a US
   - `apenas TASK-<N>`: apenas o ficheiro de task indicado
4. Criar ou atualizar `TASK-1.md` ... `TASK-K.md` (K <= 5) na pasta da US.
5. Declarar ordem e elegibilidade por task:
   - preencher `depends_on` com `[]` apenas quando a task puder iniciar sem
     predecessoras
   - usar `parallel_safe: false` como default
   - preencher `write_scope` com caminhos ou superficies concretas
6. Atualizar a secao **Tasks** do `README.md` com links relativos para cada task.
7. **Nao** alterar o manifesto da feature nem o PRD nesta sessao, salvo referencia
   cruzada explicitamente pedida pelo gate.

## Regras inegociaveis

- nunca avance para `SESSION-IMPLEMENTAR-US.md` ou `SESSION-IMPLEMENTAR-TASK.md`
  sem tasks adequadas quando `task_instruction_mode: required`
- nunca marque task como paralelizavel sem `write_scope` verificavel
- nunca grave arquivo sem `APROVADO` do agente senior *(quando o gate estiver ativo)*
- nunca alargar escopo alem da US aprovada
- preserve rastreabilidade **User Story -> Task**
- esta sessao e exclusivamente planejamento documental na fronteira **US / Task**

## Proxima etapa canonica

Execucao: `SESSION-IMPLEMENTAR-TASK.md` (task conhecida) ou
`SESSION-IMPLEMENTAR-US.md` (proxima task na fila) ate `ready_for_review`, depois
`SESSION-REVISAR-US.md`.
