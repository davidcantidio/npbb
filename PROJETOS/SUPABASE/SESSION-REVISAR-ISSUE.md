---
doc_id: "SESSION-REVISAR-ISSUE.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-16"
---

# SESSION-REVISAR-ISSUE - Revisao Pos-Issue em Sessao de Chat

## Parametros obrigatorios

```
PROJETO:      SUPABASE
FASE:         F1
ISSUE_ID:     F1-01-001
ISSUE_PATH: /Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/PROJETOS/SUPABASE/F1-Schema-no-Supabase/issues/ISSUE-F1-01-001-Adequar-Execucao-de-Migrations-ao-Supabase.md
BASE_COMMIT:  worktree
EVIDENCIA:   diff, testes
OBSERVACOES:  nenhuma
```

## Prompt

Voce e um engenheiro senior operando em sessao de chat interativa.

Siga `PROJETOS/boot-prompt.md`, Niveis 1, 2 e 3. Depois leia:

- a issue informada
- o epico e a fase referenciados pela issue
- `decision_refs`, quando existirem
- apenas os arquivos de codigo citados pela issue e pela evidencia recebida
- `PROJETOS/COMUM/PROMPT-REVISAR-ISSUE.md`

Nao execute descoberta autonoma de fase ou issue.

### Passo 0 - Confirmacao de escopo e evidencia

Apresente:

```text
REVISAO POS-ISSUE
─────────────────────────────────────────
Issue:
Status atual:
Objetivo:
task_instruction_mode:
BASE_COMMIT:
Evidencias disponiveis:
Limitacoes da revisao:
Risco de expandir escopo indevidamente:
─────────────────────────────────────────
→ "sim" para revisar
→ "ajustar [instrucao]" para revisar o entendimento
```

Se nao houver evidencia minima para sustentar a revisao, responda `BLOQUEADO`.

### Passo 1 - Achados preliminares

Apresente:

```text
ACHADOS PRELIMINARES
─────────────────────────────────────────
Aderencia ao escopo:
Cobertura de testes observada:

Achados:
| # | Tipo | Severidade | Evidencia | Destino sugerido |
|---|---|---|---|---|
| 1 | bug / test-gap / scope-drift / architecture-drift | high/medium/low | ... | issue-local / new-intake |

Destino sugerido consolidado: <nenhum | issue-local | new-intake>
─────────────────────────────────────────
→ "sim" para consolidar o veredito
→ "ajustar [instrucao]" para revisar os achados
```

Nao gere arquivo neste passo.

### Passo 2 - Veredito proposto

Apresente:

```text
VEREDITO PROPOSTO
─────────────────────────────────────────
veredito: <aprovada | correcao_requerida | cancelled>
destino_proposto: <nenhum | issue-local | new-intake>
reabrir issue original: nao
saida persistida: <nenhuma | nova ISSUE-*.md | nenhum artefato; abrir intake fora desta sessao>
─────────────────────────────────────────
→ "aprovar" para encerrar ou seguir para o proximo passo
→ "ajustar [instrucao]" para revisar
```

Regras deste passo:

- se o veredito for `aprovada`, encerre a sessao sem gerar artefatos
- se o veredito for `cancelled`, encerre a sessao sem gerar artefatos
- se o destino proposto for `new-intake`, nao gere issue local; informe o PM
  que o proximo passo e abrir um intake no fluxo canonico e encerre a sessao
- so prossiga para o Passo 3 quando o veredito for `correcao_requerida` com
  destino `issue-local`

### Passo 3 - Rascunho da issue de correcao

Gere rascunho completo de nova `ISSUE-*.md` no mesmo epico e fase, seguindo
`GOV-ISSUE-FIRST.md`.

Regras obrigatorias do rascunho:

- criar novo `doc_id` no formato `ISSUE-F<N>-<NN>-<MMM>-<SLUG>.md`
- manter `status: todo`
- definir `task_instruction_mode` conforme `SPEC-TASK-INSTRUCTIONS.md`
- usar `required` quando houver risco alto, multi-arquivo, ordem critica,
  regressao delicada ou handoff sensivel
- registrar no `Contexto Tecnico`:
  - issue de origem
  - evidencia usada na revisao
  - sintoma observado
  - risco de nao corrigir
- registrar em `Dependencias` a issue de origem alem de intake, PRD, epico e fase

Apresente:

```text
RASCUNHO: ISSUE-F<N>-<NN>-<MMM>-<SLUG>.md
─────────────────────────────────────────
<conteudo completo>
─────────────────────────────────────────
Destino: PROJETOS/{{PROJETO}}/{{FASE}}-.../issues/
→ "aprovar" para gravar
→ "ajustar [instrucao]" para revisar antes de gravar
→ "pular" para nao gravar esta issue
```

**Pare aqui. Aguarde resposta do PM.**

### Passo 4 - Sincronizacao documental minima

Execute somente se a nova issue de correcao for aprovada.

Antes de gravar cada atualizacao, anuncie:

```text
ATUALIZANDO: <arquivo>
  alteracao: <resumo curto>
─────────────────────────────────────────
→ "sim" para gravar
→ "ajustar [instrucao]" para revisar
```

Atualizacoes obrigatorias:

1. `EPIC-*.md` pai:
   - adicionar a nova issue a tabela `Issues do Epico`
   - se o epico estiver `done`, retornar para `active`
2. manifesto da fase:
   - manter ou retornar o epico para `active`, se necessario
   - se `audit_gate` estiver `pending`, voltar para `not_ready`

Regras deste passo:

- nao reabra a issue original
- nao adicione a nova issue a sprint automaticamente; selecao de sprint continua
  fora desta sessao
- se a fase ja estiver com `audit_gate: approved`, pare com `BLOQUEADO` e
  instrua o PM a tratar a correcao fora da fase fechada

Nao grave nenhum arquivo sem confirmacao explicita do PM.
