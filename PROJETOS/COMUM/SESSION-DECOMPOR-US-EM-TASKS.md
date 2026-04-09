---
doc_id: "SESSION-DECOMPOR-US-EM-TASKS.md"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-30"
---

# SESSION-DECOMPOR-US-EM-TASKS - Decomposicao User Story em Tasks

## Parametros obrigatorios

Preencha e cole junto com este prompt:

```text
PROJETO:       OPENCLAW-FRAMEWORK

US_PATH: /Users/genivalfreirenobrejunior/Documents/gh-repos/openclaw/PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-01-API-DOMINIO-CONSUMIDOR-MINIMO/README.md

FEATURE_PATH: /Users/genivalfreirenobrejunior/Documents/gh-repos/openclaw/PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-7-EXTENSAO-GOVERNANCA-COMUM-DB
PRD_PATH:      /Users/genivalfreirenobrejunior/Documents/gh-repos/openclaw/PROJETOS/OPENCLAW-FRAMEWORK-V4/PRD-OPENCLAW-FRAMEWORK-V4.md
ESCOPO:        FEATURE COMPLETA
OBSERVACOES:   NENHUMA
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

## Pre-condicao operacional: preflight do runtime e sync do indice derivado Postgres

Antes do primeiro gate desta sessao:

1. rode `../fabrica/bin/ensure-fabrica-projects-index-runtime.sh --allow-missing-url`
2. se o preflight devolver exit `0`, rode `python3 ../fabrica/scripts/fabrica.py --repo-root . sync`
3. consulte o estado da US e das tasks ja existentes no projeto apenas quando o sync tiver corrido
4. compare com o Markdown canonico; o **Markdown prevalece**
5. registre `DRIFT_INDICE: <nenhuma | descricao>` antes do primeiro gate, incluindo exit code e motivo quando o preflight falhar
6. apos gravacoes em `PROJETOS/` sob `TASK-*.md`, execute novo sync apenas se o preflight permanecer OK

Normativa complementar: `PROJETOS/COMUM/SPEC-RUNTIME-POSTGRES-MATRIX.md` (matriz
quando o sync e obrigatorio ou dispensavel, variaveis, ordem `host.env` / bootstrap / sync).

**URL ausente ou preflight falho nesta sessao:** registe `DRIFT_INDICE` descrevendo
que o sync nao correu; **nao** instale Postgres, Docker, gestores de pacotes nem
binarios externos como parte da sessao salvo pedido humano explicito; prossiga com
Markdown + Git conforme a matriz.

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

1. Validar `US_PATH` e ler o `README.md` da US por secoes/ancoras relevantes, usando `scripts/session_tools/read_file.py` antes de qualquer leitura integral.
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

- nunca avance para `SESSION-IMPLEMENTAR-US.md` sem tasks adequadas quando
  `task_instruction_mode: required`
- nunca marque task como paralelizavel sem `write_scope` verificavel
- nunca grave arquivo sem `APROVADO` do agente senior *(quando o gate estiver ativo)*
- nunca alargar escopo alem da US aprovada
- preserve rastreabilidade **User Story -> Task**
- esta sessao e exclusivamente planejamento documental na fronteira **US / Task**

## Proxima etapa canonica

Execucao: `SESSION-IMPLEMENTAR-US.md` ate `ready_for_review`, depois
`SESSION-REVISAR-US.md`.
