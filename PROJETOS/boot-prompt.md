# BOOT-PROMPT - Agente de Projeto
# Arquivo: PROJETOS/boot-prompt.md
#
# COMO USAR:
# No campo de prompt do Cursor Cloud Agent, cole apenas:
#
#   Leia PROJETOS/boot-prompt.md e execute o projeto <NOME-DO-PROJETO>
#
# O agente le este arquivo e segue as instrucoes abaixo autonomamente.
# --------------------------------------------------------------------

# Este entrypoint e exclusivo para execucao autonoma no Cloud Agent.
# Para operacao em chat interativo com confirmacoes HITL, use
# `PROJETOS/COMUM/SESSION-MAPA.md` e escolha o `SESSION-*.md` adequado.

Voce e um engenheiro senior autonomo. Sua missao e executar a proxima
unidade elegivel do projeto indicado no comando de invocacao.

O padrao canonico deste repositorio e `issue-first`, com a cadeia:

```text
Intake -> PRD -> Fases -> Epicos -> Issues -> Tasks -> Auditorias
```

A entrega executavel vive em um recurso proprio dentro de `issues/`:

- preferencialmente uma pasta `ISSUE-*/` com `README.md` e `TASK-*.md`
- por compatibilidade, um arquivo unico `ISSUE-*.md`

A auditoria de fase vive em `auditorias/RELATORIO-AUDITORIA-F<N>-R<NN>.md`
e registra sua trilha em `AUDIT-LOG.md`.

Se o projeto indicado nao estiver no padrao canonico, reporte `BLOQUEADO` e pare.

Siga rigorosamente a ordem de leitura abaixo antes de escrever qualquer
linha de codigo. Cada nivel depende do anterior.

---

## ORDEM DE LEITURA OBRIGATORIA

### Nivel 1 - Ambiente

```
AGENTS.md
```

Tudo o que estiver em `AGENTS.md` tem precedencia sobre convencoes gerais.

### Nivel 2 - Governanca

Leia estes arquivos, nesta ordem:

```
PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md
PROJETOS/COMUM/GOV-SCRUM.md
PROJETOS/COMUM/GOV-SPRINT-LIMITES.md
PROJETOS/COMUM/GOV-WORK-ORDER.md
PROJETOS/COMUM/GOV-ISSUE-FIRST.md
PROJETOS/COMUM/SPEC-TASK-INSTRUCTIONS.md
PROJETOS/COMUM/GOV-COMMIT-POR-TASK.md
PROJETOS/COMUM/GOV-INTAKE.md
PROJETOS/COMUM/GOV-AUDITORIA.md
```

### Nivel 3 - Projeto

Leia, nesta ordem:

```
PROJETOS/<PROJETO>/INTAKE-<PROJETO>.md
PROJETOS/<PROJETO>/PRD-<PROJETO>.md
PROJETOS/<PROJETO>/AUDIT-LOG.md
```

Entenda a origem da iniciativa, o objetivo, o escopo, a arquitetura, os riscos,
as fases previstas, as restricoes e o historico de auditorias do projeto.

### Nivel 4 - Fases

Leia as fases na ordem `F1 -> F2 -> F3...` usando o arquivo:

```
PROJETOS/<PROJETO>/F<N>-<NOME>/F<N>_<PROJETO>_EPICS.md
```

Para cada fase:

- se a fase estiver `done` e o gate de auditoria estiver `approved`, avance para a proxima fase
- se todos os epicos da fase estiverem `done` e o gate de auditoria nao estiver `approved`, entre em modo `AUDITORIA`
- se existe epico `active`, este e o epico de trabalho
- se existe epico `todo` e a fase anterior estiver concluida com auditoria `go`, este e o proximo epico elegivel
- se a fase anterior nao concluiu ou estiver sem auditoria aprovada, reporte `BLOQUEADO` e pare

### Nivel 5 - Epico ativo ou fase em auditoria

Para execucao de issue, leia:

```
PROJETOS/<PROJETO>/F<N>-<NOME>/EPIC-F<N>-<NN>-<NOME>.md
```

Use o epico para entender objetivo, DoD, dependencias e indice das issues.

Para auditoria de fase, leia:

```
PROJETOS/<PROJETO>/F<N>-<NOME>/auditorias/
```

Se ja existir auditoria anterior da fase, leia tambem o relatorio mais recente,
os follow-ups apontados no `AUDIT-LOG.md` e qualquer `INTAKE-*` derivado por `hold`
antes de prosseguir.

### Nivel 6 - Unidade elegivel

#### Modo ISSUE

Leia apenas a proxima issue elegivel:

```
PROJETOS/<PROJETO>/F<N>-<NOME>/issues/ISSUE-F<N>-<NN>-<MMM>-<NOME>/
ou
PROJETOS/<PROJETO>/F<N>-<NOME>/issues/ISSUE-F<N>-<NN>-<MMM>-<NOME>.md
```

Selecione a primeira issue cujo status esteja `todo` ou `active` e cujas
dependencias estejam satisfeitas.

Resolva o formato da issue antes de executar:

- se existir a pasta `ISSUE-*/`, trate a issue como granularizada: leia
  `README.md` e todos os `TASK-*.md`
- se existir apenas o arquivo `ISSUE-*.md`, trate a issue como legada

Antes de implementar, leia `task_instruction_mode` no frontmatter do
`README.md` ou do arquivo da issue.

- se `task_instruction_mode` estiver ausente, assuma `optional` por compatibilidade
- se a issue for granularizada, use o `README.md` como manifesto e selecione a
  primeira `TASK-N.md` com `status: todo` ou `active`; execute apenas essa task
- se `task_instruction_mode` for `required` em issue granularizada, valide que
  cada `TASK-N.md` tem os campos minimos de `TEMPLATE-TASK.md`
- se `task_instruction_mode` for `required` em issue legada, valide a secao
  `## Instructions por Task`
- se a task selecionada tiver `tdd_aplicavel: true`, valide que `testes_red`
  existe, que inclui testes a escrever primeiro, comando red e criterio explicito
  de falha inicial, e que `passos_atomicos` segue a ordem red -> green -> refactor
- se faltar o detalhamento obrigatorio do formato escolhido, reporte
  `BLOQUEADO` e pare

Antes de implementar, leia tambem os arquivos de codigo explicitamente citados
no manifesto da issue e na task selecionada.

#### Modo AUDITORIA

Crie ou atualize a proxima rodada elegivel:

```
PROJETOS/<PROJETO>/F<N>-<NOME>/auditorias/RELATORIO-AUDITORIA-F<N>-R<NN>.md
```

Use como insumos minimos o `INTAKE-*.md`, o `PRD-*.md`, o manifesto da fase,
os epicos e issues da fase, o `AUDIT-LOG.md`, o ultimo relatorio da fase
(se existir), os diffs relevantes, os testes executados e o commit base auditado.

---

## CONFIRMACAO ANTES DE IMPLEMENTAR

Apos completar a leitura, reporte:

```text
MODO:              ISSUE / AUDITORIA
PROJETO:           <nome>
FASE ALVO:         F<N> - <nome>
EPICO ALVO:        EPIC-F<N>-<NN> - <nome> / n-a
UNIDADE ELEGIVEL:  ISSUE-F<N>-<NN>-<MMM> - <nome> / AUDITORIA-F<N>-R<NN>
TASK ALVO:         T<N> / n-a
TASK_INSTR_MODE:   optional / required / n-a
SP:                <valor> / n-a
DEPENDENCIAS:      <satisfeitas / bloqueadas>
DECISAO:           PROSSEGUIR / BLOQUEADO
```

Se `BLOQUEADO`: pare e explique o motivo.
Se `PROSSEGUIR`: avance para a execucao da unidade elegivel.

---

## EXECUCAO

Principios obrigatorios:

- implementar exatamente o que os criterios de aceitacao descrevem
- nao aumentar escopo sem aprovacao explicita
- pensar na arquitetura antes de codificar
- priorizar modularidade, responsabilidade unica, baixo acoplamento e alta coesao
- escrever ou atualizar testes conforme indicado na issue
- nao emitir veredito `go` em auditoria sem commit SHA e arvore limpa

### Sequencia minima para ISSUE

1. Confirmar entendimento do escopo
2. Se a issue for granularizada, executar apenas a proxima `TASK-N.md`; se for
   legada com `task_instruction_mode: required`, executar cada task seguindo
   sua instrucao atomica inline
3. Se a task alvo tiver `tdd_aplicavel: true`, executar primeiro o red da task:
   escrever os testes descritos em `testes_red`, rodar o comando declarado e
   confirmar que os testes falham antes de alterar codigo; se nao falharem,
   reportar `BLOQUEADO`
4. So depois do red confirmado implementar o minimo necessario para a task,
   rerodar a suite alvo e confirmar green antes de refatorar
5. **Apos cada task concluida**, atualizar o status da task correspondente e o
   status agregado da issue, depois fazer commit com mensagem descritiva conforme
   `GOV-COMMIT-POR-TASK.md` (PROJETO, ISSUE_ID, TASK_ID, descricao breve)
6. Executar `Red`, `Green` e `Refactor` conforme o `README.md` da issue ou o
   arquivo legado, respeitando o detalhamento da task quando `tdd_aplicavel: true`
7. Rodar os testes diretamente relacionados
8. Registrar desvios como proposta de decisao quando necessario

### Sequencia minima para AUDITORIA

1. Confirmar escopo auditado e commit base
2. Ler `AUDIT-LOG.md` e o ultimo relatorio da fase, se existirem
3. Auditar aderencia a `INTAKE`, `PRD`, fase, epicos, issues e testes
4. Avaliar bugs, code smells, arquivos/funcoes monoliticas, docstrings relevantes, gaps de testes e drift arquitetural
5. Classificar achados com categoria e severidade
6. Emitir veredito `go`, `hold` ou `cancelled` com evidencias e follow-ups

Regras de ambiente:

```text
PYTHONPATH=/workspace:/workspace/backend
Testes backend : TESTING=true SECRET_KEY=ci-secret-key python -m pytest -q
Testes frontend: cd frontend && npm run test -- --run
Lint           : cd backend && ruff check app tests
Migrations     : alembic upgrade head deve passar sem erro
```

---

## FINALIZACAO

### Ao concluir uma ISSUE

1. Se a issue for granularizada, atualize o `TASK-N.md` executado e recalcule o
   `README.md` com o status agregado (`active` quando ainda houver task aberta;
   `done` quando todas as tasks estiverem `done`); se for legada, atualize o
   arquivo `ISSUE-*.md`
2. Marque o `Definition of Done` no `README.md` da issue ou no arquivo legado
3. Atualize a tabela de issues do `EPIC-*.md`
4. Recalcule o status do epico e mantenha a fase `active` ate o fechamento do gate de auditoria
5. Se todos os epicos da fase estiverem `done`, atualize o gate de auditoria da fase para `pending`

### Ao concluir uma AUDITORIA

1. Atualize ou crie `auditorias/RELATORIO-AUDITORIA-F<N>-R<NN>.md`
2. Registre a rodada em `AUDIT-LOG.md`
3. Atualize o gate de auditoria no manifesto da fase (`not_ready`, `pending`, `hold`, `approved`)
4. Se o veredito for `hold`, escolha o destino do follow-up:
   - `issue-local` para correcao local e contida na mesma fase
   - `new-intake` para remediacao estrutural ou sistemica, abrindo `INTAKE-<PROJETO>-<SLUG>.md` com `intake_kind: audit-remediation`
5. Se o veredito for `go`, atualize o status da fase para `done` e mova a pasta inteira da fase para `<projeto>/feito/` no mesmo change set que atualiza os links internos

`BLOQUEADO` e `BLOCKED_LIMIT` sao estados operacionais de execucao. Eles nao entram na lista de status canonicos persistidos nos documentos.

Se for abrir PR:

- titulo sugerido: `feat: <nome da issue> (<ISSUE-ID>)`
- corpo: checklist dos criterios de aceitacao da issue ou checklist do relatorio de auditoria
