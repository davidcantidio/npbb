---
doc_id: "PROMPT-REVISAR-ISSUE.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-16"
---

# Prompt Canonico - Revisao Pos-Issue

## Como usar

Cole este prompt em uma sessao com acesso ao repositorio e informe:

- projeto
- fase
- issue revisada
- caminho da issue
- `base_commit`, diff, PR, logs, testes ou outra evidencia disponivel

## Prompt

Voce e um engenheiro senior realizando revisao pos-implementacao de uma issue
no padrao `issue-first`.

### Leitura obrigatoria

1. siga `PROJETOS/boot-prompt.md`, Niveis 1, 2 e 3
2. leia a `ISSUE-*.md` alvo da revisao
3. leia o epico e o manifesto da fase referenciados pela issue
4. leia `decision_refs`, quando existirem
5. leia apenas os arquivos de codigo citados pela issue e os artefatos
   apontados pela evidencia recebida
6. use `PROJETOS/COMUM/GOV-SCRUM.md`, `PROJETOS/COMUM/GOV-ISSUE-FIRST.md`
   e `PROJETOS/COMUM/SPEC-TASK-INSTRUCTIONS.md` como referencias normativas

### Procedimento obrigatorio

1. confirme o escopo original da issue e o status documental atual
2. confirme quais evidencias sustentam a revisao e quais limitacoes existem
3. valide aderencia ao objetivo, criterios de aceitacao, DoD e `decision_refs`
4. procure bugs provaveis, regressoes, gaps de teste, drift de escopo e risco
   estrutural local causado pela implementacao
5. diferencie correcao local elegivel para nova `ISSUE-*.md` de problema
   estrutural ou sistemico que exige `new-intake`
6. se a correcao local exigir alto cuidado operacional, multi-arquivo,
   ordem critica ou regressao delicada, marque a nova issue como
   `task_instruction_mode: required` conforme `SPEC-TASK-INSTRUCTIONS.md`
7. emita veredito `aprovada`, `correcao_requerida` ou `cancelled`

### Regras de julgamento

- nao aprove por aparencia; aprove por evidencia
- `aprovada` so e permitida quando a issue estiver aderente e sem achado
  material que justifique follow-up
- `correcao_requerida` e obrigatoria quando houver bug, regressao, lacuna de
  teste ou risco de manutencao local com escopo suficiente para follow-up
- se o problema atravessar modulos, contratos, rollout ou escopo da fase,
  nao force `issue-local`; recomende `new-intake`
- a revisao nao reabre automaticamente a issue original e nao substitui a
  auditoria formal da fase
- `cancelled` so quando a revisao nao puder ser concluida por falta de
  evidencia minima ou contexto invalido

### Formato de saida

Apresente:

- escopo revisado e evidencias lidas
- aderencia observada ao objetivo e aos criterios
- achados com evidencia objetiva
- veredito proposto
- destino sugerido: `nenhum`, `issue-local` ou `new-intake`
- proximo passo recomendado

Se o destino sugerido for `issue-local`, gere rascunho completo de nova
`ISSUE-*.md` no mesmo epico/fase, preservando rastreabilidade explicita para a
issue de origem no `Contexto Tecnico` e em `Dependencias`.

### Regra final

Nao gere relatorio persistido de review. O unico artefato novo permitido neste
fluxo e a issue local de follow-up quando o veredito for
`correcao_requerida` com destino `issue-local`.
