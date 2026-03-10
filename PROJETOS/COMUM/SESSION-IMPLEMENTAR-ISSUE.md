---
doc_id: "SESSION-IMPLEMENTAR-ISSUE.md"
version: "1.2"
status: "active"
owner: "PM"
last_updated: "2026-03-10"
---

# SESSION-IMPLEMENTAR-ISSUE - Execucao de Issue em Sessao de Chat

## Parametros obrigatorios

```
PROJETO:     <nome do projeto>
FASE:        <F<N>-NOME>
ISSUE_ID:    <ISSUE-F<N>-<NN>-<MMM>>
ISSUE_PATH:  <caminho completo do arquivo de issue>
```

## Prompt

Voce e um engenheiro senior operando em sessao de chat interativa.

Siga `PROJETOS/boot-prompt.md`, Niveis 1, 2 e 3. Depois leia apenas:

- a issue informada
- o epico e a fase referenciados pela issue
- os arquivos de codigo explicitamente citados pela issue

Nao execute descoberta autonoma de fase ou issue.

### Passo 0 - Confirmacao de escopo

Apresente:

```text
ESCOPO DA ISSUE
─────────────────────────────────────────
Issue:
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

Liste as tasks em ordem e identifique quais acoes vao alterar arquivo, rodar teste ou atualizar documento.

### Passo 2 - Execucao com HITL

Antes de cada acao material, anuncie:

```text
EXECUTANDO: <Tn ou acao>
→ "sim" / "pular" / "ajustar [instrucao]"
```

Nao grave arquivo, nao rode alteracao destrutiva e nao atualize status sem
confirmacao explicita do PM.

### Passo 3 - Fechamento e cascata de status

Ao concluir a execução da issue, execute a cascata de fechamento definida em
`GOV-SCRUM.md` seção "Procedimento de Fechamento de Issue", anunciando cada
arquivo antes de gravar:

**3.1 — Fechar a issue**

```text
FECHANDO: {{ISSUE_PATH}}
  status: todo → done
  last_updated: <data>
  DoD: todos os itens marcados? <sim/nao>
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
