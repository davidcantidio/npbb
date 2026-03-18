---
doc_id: "SESSION-REVISAR-ISSUE.md"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-16"
---

# SESSION-REVISAR-ISSUE - Revisao Pos-Issue em Sessao de Chat

## Parametros obrigatorios

```
PROJETO: DASHBOARD-LEADS
FASE: F1-CONSOLIDACAO-VINCULO-CANONICO
ISSUE_ID: ISSUE-F1-01-001
ISSUE_PATH: /Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/PROJETOS/DASHBOARD-LEADS/F1-CONSOLIDACAO-VINCULO-CANONICO/issues/ISSUE-F1-01-001-CORRIGIR-SURFACE-DE-MODELO-E-BOOT-DA-APP
BASE_COMMIT: c81dddcbb5c9
TARGET_COMMIT:e129279
EVIDENCIA: git show e129279; log da suite alvo cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_dashboard_age_analysis_endpoint.py tests/test_dashboard_leads_endpoint.py tests/test_dashboard_leads_report_endpoint.py
OBSERVACOES: revisar como implementacao parcial/prematura; a issue original permanece todo e o commit evidencia apenas teste de regressao em backend/tests/test_dashboard_leads_endpoint.py, sem a correcao em backend/app/models/models.py
```

## Prompt

Voce e um engenheiro senior operando em sessao de chat interativa.

Siga `PROJETOS/boot-prompt.md`, Niveis 1, 2 e 3. Depois leia:

- a issue informada (se for pasta, leia `README.md` e os `TASK-*.md` para revisao)
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
saida persistida: <nenhuma | nova ISSUE-*/ com README.md + TASK-*.md | nova ISSUE-*.md | nenhum artefato; abrir intake fora desta sessao>
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

Gere rascunho completo de novo recurso de issue local no mesmo epico e fase,
seguindo `GOV-ISSUE-FIRST.md`.

Regras obrigatorias do rascunho:

- usar issue granularizada como padrao: criar pasta
  `ISSUE-F<N>-<NN>-<MMM>-<SLUG>/` com `README.md` e `TASK-*.md` quando houver
  multiplas tasks, tarefas decupadas ou `task_instruction_mode: required`
- usar arquivo unico `ISSUE-F<N>-<NN>-<MMM>-<SLUG>.md` apenas quando a
  correcao for simples, local e de task unica
- se a issue for granularizada, usar `README.md` como manifesto e
  `PROJETOS/COMUM/TEMPLATE-TASK.md` para cada `TASK-N.md`
- manter no manifesto da issue: user story, contexto tecnico, plano TDD,
  criterios, DoD, tasks, arquivos reais e artefato minimo
- criar `doc_id` coerente com o formato escolhido:
  - issue granularizada: `doc_id` do `README.md` igual ao identificador da issue
  - issue legada: `doc_id` no formato `ISSUE-F<N>-<NN>-<MMM>-<SLUG>.md`
- manter `status: todo`
- definir `task_instruction_mode` conforme `SPEC-TASK-INSTRUCTIONS.md`
- usar `required` quando houver risco alto, multi-arquivo, ordem critica,
  regressao delicada ou handoff sensivel
- quando uma task envolver codigo novo ou alteracao com cobertura automatizavel,
  marcar `tdd_aplicavel: true` e preencher `testes_red` + `passos_atomicos`
  na ordem red -> green -> refactor; quando nao envolver TDD, manter
  `tdd_aplicavel: false` ou omitir conforme a spec
- registrar no `Contexto Tecnico`:
  - issue de origem
  - evidencia usada na revisao
  - sintoma observado
  - risco de nao corrigir
- registrar em `Dependencias` a issue de origem alem de intake, PRD, epico e fase

Apresente:

```text
RASCUNHO: ISSUE-F<N>-<NN>-<MMM>-<SLUG>/ (pasta) ou ISSUE-F<N>-<NN>-<MMM>-<SLUG>.md (arquivo legado)
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
   - apontar o campo `Documento` para a pasta `./issues/ISSUE-.../` ou para o
     arquivo legado correspondente
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
