---
doc_id: "TASK-4.md"
user_story_id: "US-4-06-SUPERFICIE-CONCILIACAO-BLOQUEIOS"
task_id: "T4"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T2"
parallel_safe: false
write_scope:
  - "frontend/src/pages/ativos/AtivosConciliacaoPage.tsx"
  - "frontend/src/services/ativos_recebimento.ts"
tdd_aplicavel: false
---

# TASK-4 - Registo de recebimento na UI (condicional ao desenho)

## objetivo

Se o desenho de produto previr entrada de **recebido confirmado** pela UI, implementar o fluxo (formulario ou modal) que chama a API da [US-4-02](../US-4-02-REGISTRO-RECEBIDO-CONFIRMADO/README.md), respeita validacoes do backend e apresenta feedback utilizavel; caso contrario, **cancelar** esta task com justificativa no relatorio de execucao e garantir que a US ainda cumpre os criterios 1–2 apenas com leitura.

## precondicoes

- [T2](./TASK-2.md) concluida (`done`) *(fluxo contextualizado na vista de conciliacao)*.
- Decisao explicita por escrito (comentario em issue, ADR ou anexo da US) sobre se a UI deve registar recebimento ou apenas consumir dados.
- Endpoint POST/PATCH (ou equivalente) da US-4-02 disponivel e documentado.

## orquestracao

- `depends_on`: `["T2"]`.
- `parallel_safe`: false.
- `write_scope`: mesmo modulo que conciliacao e servico HTTP; coordenar com [T3](./TASK-3.md) se ambas alterarem `ativos_recebimento.ts` na mesma janela (preferir sequencia T3 antes de T4 ou vice-versa conforme plano de merge).

## arquivos_a_ler_ou_tocar

- `frontend/src/pages/ativos/AtivosConciliacaoPage.tsx`
- `frontend/src/services/ativos_recebimento.ts`
- Manifesto [US-4-02](../US-4-02-REGISTRO-RECEBIDO-CONFIRMADO/README.md) e requisitos de auditoria [US-4-01](../US-4-01-MODELO-PERSISTENCIA-RECEBIMENTO/README.md)

## passos_atomicos

1. Se **nao** houver desenho aprovado para registo na UI: marcar task `cancelled`, documentar motivo e parar (criterio 3 da US fica fora de escopo por decisao de produto).
2. Caso contrario: mapear payload obrigatorio (evento, categoria, quantidades, artefatos/metadata conforme US-4-02).
3. Implementar chamada HTTP no servico e UI com validacao client-side minima espelhando o servidor, mensagens de erro claras e sucesso com resumo.
4. Apos sucesso, disparar refetch da conciliacao (e indicar ao utilizador que pode verificar bloqueios na vista da T3).
5. Nao persistir dados sensiveis fora do contrato; seguir quaisquer limites LGPD descritos no PRD.

## comandos_permitidos

- `cd frontend && npm run typecheck`
- `cd frontend && npm run lint`

## resultado_esperado

Criterio de aceite 3 da US satisfeito **ou** task cancelada com justificativa e US validada apenas nos criterios 1–2.

## testes_ou_validacoes_obrigatorias

- `cd frontend && npm run typecheck`.
- Teste manual: submissao valida e caso de erro de validacao devolvido pelo backend; confirmar que a trilha de auditoria fica a cargo do backend (US-4-01) e que a UI nao omite identificadores necessarios ao correlacionar.

## stop_conditions

- Parar e cancelar a task se nao existir decisao de desenho ou endpoint US-4-02.
- Parar se o backend nao devolver erros acoes — nao mascarar falhas com sucesso falso.
