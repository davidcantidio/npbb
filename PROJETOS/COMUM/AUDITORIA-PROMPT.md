---
doc_id: "AUDITORIA-PROMPT.md"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-08"
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

1. `AGENTS.md`
2. `PROJETOS/COMUM/scrum-framework-master.md`
3. `PROJETOS/COMUM/SCRUM-GOV.md`
4. `PROJETOS/COMUM/WORK-ORDER-SPEC.md`
5. `PROJETOS/COMUM/AUDITORIA-GOV.md`
6. `PROJETOS/<PROJETO>/INTAKE-*.md` relevante ao escopo
7. `PROJETOS/<PROJETO>/PRD-*.md`
8. `PROJETOS/<PROJETO>/AUDIT-LOG.md`
9. `PROJETOS/<PROJETO>/<FASE>/F<N>_<PROJETO>_EPICS.md`
10. epicos e issues da fase
11. ultimo relatorio da fase, se existir

### Procedimento obrigatorio

1. confirme o commit base auditado
2. verifique se a arvore esta limpa
3. se a arvore estiver suja, marque a auditoria como `provisional`
4. valide aderencia ao intake, PRD, manifesto da fase, epicos e issues
5. inspecione bugs provaveis, regressoes, code smells, arquivos monoliticos, funcoes monoliticas, gaps de testes e ausencia de docstrings em codigo compartilhado, publico ou complexo
6. classifique cada achado com categoria e severidade
7. diferencie follow-up `issue-local` de `new-intake` conforme o escopo da remediacao
8. emita veredito `go`, `hold` ou `cancelled`

### Regras de julgamento

- nao aprove por simpatia; aprove por evidencia
- `go` so e permitido com aderencia suficiente, testes coerentes e commit SHA valido
- `hold` e obrigatorio quando houver desvio material, risco relevante sem cobertura ou lacuna de rastreabilidade
- ausencia isolada de docstring nao bloqueia por si so; so bloqueia quando agrava codigo complexo, compartilhado ou de manutencao dificil
- `cancelled` so quando a rodada nao puder ser concluida por falta de insumo ou contexto invalido

### Formato de saida

Use o template `PROJETOS/COMUM/AUDITORIA-REPORT-TEMPLATE.md` e preencha:

- resumo executivo
- evidencias lidas
- conformidades
- nao conformidades
- saude estrutural do codigo
- bugs e riscos antecipados
- cobertura de testes
- decisao final
- follow-ups bloqueantes e nao bloqueantes
- handoff para novo intake quando houver remediacao estrutural

### Regra final

Se houver auditoria anterior com `hold`, voce deve ler o ultimo relatorio, verificar explicitamente se os follow-ups foram resolvidos e manter a rastreabilidade entre relatorio, log e novo intake quando a remediacao for estrutural.
