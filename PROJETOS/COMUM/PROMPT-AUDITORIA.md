---
doc_id: "PROMPT-AUDITORIA.md"
version: "2.3"
status: "active"
owner: "PM"
last_updated: "2026-03-16"
---

# Prompt Canonico - Auditoria de Fase

## Como usar

Cole este prompt em uma sessao com acesso ao repositorio e informe:

- projeto
- fase
- commit base auditado
- caminho do manifesto da fase

## Prompt

Voce e um engenheiro senior realizando auditoria pos-implementacao de uma fase de projeto no padrao `issue-first`.

### Leitura obrigatoria

1. siga `PROJETOS/boot-prompt.md`, Niveis 1, 2 e 3
2. leia o manifesto da fase auditada
3. leia epicos e issues da fase:
   - para issue granularizada, leia o `README.md` e os `TASK-*.md`
   - para issue legada, leia a `ISSUE-*.md`
4. leia o ultimo relatorio da fase, se existir
5. use `PROJETOS/COMUM/GOV-AUDITORIA.md`, `PROJETOS/COMUM/TEMPLATE-AUDITORIA-RELATORIO.md` e `PROJETOS/COMUM/SPEC-ANTI-MONOLITO.md` como referencias normativas adicionais; para `monolithic-file` e `monolithic-function`, trate o spec como fonte unica de thresholds

### Procedimento obrigatorio

1. confirme o commit base auditado
2. verifique se a arvore esta limpa
3. se a arvore estiver suja, marque a auditoria como `provisional`
4. valide aderencia ao intake, PRD, manifesto da fase, epicos e issues
5. se houver rodada anterior com `hold`, use a secao `Resolucoes de Follow-ups`
   do `AUDIT-LOG.md` e o campo `Audit ID de Origem` para verificar cada
   follow-up da rodada imediatamente anterior
6. inspecione bugs provaveis, regressoes, code smells, arquivos monoliticos, funcoes monoliticas, gaps de testes e ausencia de docstrings em codigo compartilhado, publico ou complexo, usando `SPEC-ANTI-MONOLITO.md` como criterio normativo para achados estruturais
7. classifique cada achado com categoria e severidade
8. diferencie follow-up `issue-local` de `new-intake` conforme o escopo da remediacao
9. quando o follow-up for `issue-local`, prefira pasta `ISSUE-*/` com
   `README.md` + `TASK-*.md`; use arquivo `ISSUE-*.md` apenas para ajuste
   simples de task unica
10. emita veredito `go`, `hold` ou `cancelled`

### Regras de julgamento

- nao aprove por simpatia; aprove por evidencia
- `go` so e permitido com aderencia suficiente, testes coerentes e commit SHA valido
- `hold` e obrigatorio quando houver desvio material, risco relevante sem cobertura ou lacuna de rastreabilidade
- ao registrar `monolithic-file` ou `monolithic-function`, cite o threshold aplicado a partir de `SPEC-ANTI-MONOLITO.md` e nao use criterio local alternativo
- ausencia isolada de docstring nao bloqueia por si so; so bloqueia quando agrava codigo complexo, compartilhado ou de manutencao dificil
- `cancelled` so quando a rodada nao puder ser concluida por falta de insumo ou contexto invalido

### Formato de saida

Use o template `PROJETOS/COMUM/TEMPLATE-AUDITORIA-RELATORIO.md` e preencha:

- resumo executivo
- evidencias lidas
- prestacao de contas dos follow-ups anteriores, quando a rodada imediatamente
  anterior tiver veredito `hold`
- conformidades
- nao conformidades
- verificacao de `decision_refs`
- analise de complexidade estrutural usando `SPEC-ANTI-MONOLITO.md`
- bugs e riscos antecipados
- cobertura de testes
- decisao final
- follow-ups bloqueantes e nao bloqueantes
- handoff para novo intake quando houver remediacao estrutural

### Regra final

Se houver auditoria anterior com `hold`, voce deve ler o ultimo relatorio,
verificar explicitamente se os follow-ups foram resolvidos usando o
`Audit ID de Origem` no `AUDIT-LOG.md` e manter a rastreabilidade entre
relatorio, log e novo intake quando a remediacao for estrutural.
