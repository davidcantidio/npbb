---
doc_id: "SESSION-IMPLEMENTAR-ISSUE.md"
version: "1.6"
status: "active"
owner: "PM"
last_updated: "2026-03-16"
---

# SESSION-IMPLEMENTAR-ISSUE - Execucao de Issue em Sessao de Chat

## Parametros de entrada

```
PROJETO:     <nome do projeto>
FASE:        <F<N>-NOME>
ISSUE_ID:    <ISSUE-F<N>-<NN>-<MMM>>
ISSUE_PATH:  <caminho completo: arquivo ISSUE-*.md ou pasta ISSUE-*/ com README.md>
TASK_ID:     <opcional: T<N> ou "auto">
```

## Prompt

Voce e um engenheiro senior operando em sessao de chat interativa.

Siga `PROJETOS/boot-prompt.md`, Niveis 1, 2 e 3. Depois leia apenas:

- a issue informada
- o epico e a fase referenciados pela issue
- os arquivos de codigo explicitamente citados pela issue

Nao execute descoberta autonoma de fase ou issue.

**Deteccao de formato:** Se `ISSUE_PATH` apontar para uma pasta (termina em `/` ou e um
diretorio), a issue e granularizada: leia `README.md` e liste `TASK-*.md`. Se apontar para
arquivo `.md`, a issue e legada: leia o arquivo e as tasks estao no corpo.

Se `TASK_ID` for informado, a execucao fica restrita a essa task especifica. Se
`TASK_ID: auto` ou o parametro estiver ausente, selecione a proxima task
elegivel normalmente.

### Passo 0 - Confirmacao de escopo

Apresente:

```text
ESCOPO DA ISSUE
─────────────────────────────────────────
Issue:
Task alvo:
Objetivo:
Dependencias:
task_instruction_mode:
Riscos:
─────────────────────────────────────────
→ "sim" para preparar a execucao
→ "ajustar [instrucao]" para revisar o entendimento
```

Se `task_instruction_mode: required` estiver incompleto, responda `BLOQUEADO`.

**Verificacao de defasagem de estado de auditoria**

Se a issue referenciar um relatorio de auditoria de origem (campo `Auditoria de
Origem` nas dependencias ou `origin_audit_id`), execute esta verificacao antes
de prosseguir:

1. leia o `AUDIT-LOG.md` do projeto
2. compare o estado atual do gate da fase com o estado assumido pela issue
3. verifique se existe rodada de auditoria posterior a referenciada pela issue

Se houver rodada posterior:

```text
ALERTA — DEFASAGEM DE ESTADO DE AUDITORIA
─────────────────────────────────────────
Issue assume: <rodada X, gate Y>
Estado atual: <rodada Z, gate W>

Rodada posterior encontrada: <ID>
  veredito: <go | hold>
  data: <data>

Situacoes possiveis:
  A) a issue foi superada pela rodada posterior e nao precisa ser executada
  B) a issue ainda e valida mas suas instrucoes estao desatualizadas
  C) a rodada posterior foi executada prematuramente com esta issue ainda aberta

Nao e possivel determinar automaticamente qual situacao se aplica.
─────────────────────────────────────────
→ "situacao A" para encerrar a issue como cancelled com justificativa
→ "situacao B" para prosseguir ciente da defasagem — PM assume responsabilidade
→ "situacao C" para parar e escalar ao PM sem alterar nenhum arquivo
```

**Pare aqui. Aguarde resposta do PM antes de qualquer execucao.**

### Passo 1 - Plano de execucao

- **Issue granularizada (pasta):** Liste os `TASK-*.md` em ordem. Se `TASK_ID` foi informado,
  valide que o `TASK-N.md` correspondente existe e esta `todo` ou `active`; se nao estiver,
  responda `BLOQUEADO`. Sem `TASK_ID`, identifique a proxima task com `status: todo` ou
  `active`. Execute apenas essa task; ao concluir, atualize `status: done` no `TASK-N.md`,
  recalcule o status agregado no `README.md` (`active` se ainda houver task aberta; `done`
  apenas quando todas estiverem encerradas), e faca commit; se todas as tasks estiverem done,
  execute a cascata de fechamento. Se a task alvo tiver `tdd_aplicavel: true`, o plano de
  execucao deve explicitar as subfases `red`, `green` e `refactor` antes de qualquer mudanca de
  codigo.
- **Issue legada (arquivo):** Liste as tasks em ordem. Se `TASK_ID` foi informado, valide que
  existe bloco correspondente e que a task nao esta encerrada; se nao existir, responda
  `BLOQUEADO`. Sem `TASK_ID`, identifique a proxima task elegivel. Em ambos os casos, execute
  apenas uma task por vez e identifique quais acoes vao alterar arquivo, rodar teste ou
  atualizar documento. Se a task alvo tiver `tdd_aplicavel: true`, o plano de execucao deve
  explicitar as subfases `red`, `green` e `refactor`.

### Passo 2 - Execucao com HITL

Antes de cada acao material, anuncie:

```text
EXECUTANDO: <Tn ou acao>
→ "sim" / "pular" / "ajustar [instrucao]"
```

Quando a task tiver `tdd_aplicavel: true`, siga obrigatoriamente esta ordem antes de implementar:

1. escrever os testes descritos em `testes_red`
2. rodar o comando de `testes_red` e confirmar falha real ligada ao gap da task
3. se os testes nao falharem, parar e reportar bloqueio ou inconsistência de task
4. so depois da falha confirmada implementar o codigo minimo para fazer a suite passar
5. rodar novamente a suite alvo, confirmar green e so entao refatorar se necessario

**Apos cada task concluida**, antes de prosseguir para a proxima task ou para o
fechamento, sincronize os status documentais e faca commit com mensagem
descritiva conforme `GOV-COMMIT-POR-TASK.md`:

- issue granularizada:
  - atualizar o `TASK-N.md` para `done`
  - atualizar o `README.md` para `active` quando ainda restar task `todo` ou `active`
  - atualizar o `README.md` para `done` apenas quando todas as tasks estiverem `done`
- issue legada:
  - atualizar o checklist/task correspondente no proprio arquivo

```text
COMMIT: <PROJETO> <ISSUE_ID> <TASK_ID>: <descricao breve>
Ex.: LP ISSUE-F1-01-001 T1: criar modelo Ativacao em models.py
```

Nao grave arquivo, nao rode alteracao destrutiva e nao atualize status sem
confirmacao explicita do PM.

### Passo 3 - Fechamento e cascata de status

Ao concluir a execução da issue, execute a cascata de fechamento definida em
`GOV-SCRUM.md` seção "Procedimento de Fechamento de Issue", anunciando cada
arquivo antes de gravar:

**3.1 — Fechar a issue**

- **Issue granularizada:** atualizar `README.md` da pasta com `status: done` e `last_updated`.
- **Issue legada:** atualizar o arquivo da issue.

```text
FECHANDO: {{ISSUE_PATH}} (ou README.md da pasta)
  status: <todo|active> → done
  last_updated: <data>
  DoD: todos os itens marcados? <sim/nao>
  (granularizada: todas as tasks done? <sim/nao>)
─────────────────────────────────────────
→ "sim" para gravar
→ "ajustar [instrucao]"
```

**3.2 — Atualizar o épico pai**

Abra o `EPIC-*.md` referenciado pela issue. Atualize a linha da issue na tabela.
Verifique se todas as issues do épico estão `done`.

```text
ATUALIZANDO: <caminho do EPIC-*.md>
  linha da issue na tabela: status → done
  todas as issues do épico done? <sim/nao>
  → épico: <todo→active | active→active | active→done>
─────────────────────────────────────────
→ "sim" para gravar
→ "ajustar [instrucao]"
```

**3.3 — Atualizar o manifesto da fase**

Abra o `F<N>_<PROJETO>_EPICS.md`. Atualize a linha do épico na tabela.
Verifique se todos os épicos da fase estão `done`.

```text
ATUALIZANDO: <caminho do manifesto da fase>
  linha do épico na tabela: status → <novo status>
  todos os épicos da fase done? <sim/nao>
  → fase: <todo→active | active→active>
  → audit_gate: <mantém not_ready | not_ready→pending>
─────────────────────────────────────────
→ "sim" para gravar
→ "ajustar [instrucao]"
```

> Se `audit_gate` mudar para `pending`, informe o PM:
> *"Todos os épicos estão done. A fase está pronta para auditoria.
> Use SESSION-AUDITAR-FASE.md para iniciar a próxima rodada."*

**3.4 — Atualizar a sprint**

Abra o `SPRINT-*.md` que contém esta issue. Atualize a linha da issue na tabela.
Verifique se todas as issues da sprint estão `done` ou `cancelled`.

```text
ATUALIZANDO: <caminho do SPRINT-*.md>
  linha da issue na tabela: status → done
  todas as issues da sprint encerradas? <sim/nao>
  → sprint: <active→active | active→done>
─────────────────────────────────────────
→ "sim" para gravar
→ "ajustar [instrucao]"
```

**Não pule nenhum dos quatro passos.** Status inconsistente no épico ou no
manifesto da fase bloqueia a leitura correta pelo próximo agente ou sessão.

> Se o PM quiser uma segunda leitura apos a execucao desta issue, use
> `SESSION-REVISAR-ISSUE.md`. Essa revisao e opcional, nao substitui a
> auditoria de fase e nao reabre automaticamente a issue original.
