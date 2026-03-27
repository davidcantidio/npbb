---
doc_id: "TASK-2.md"
user_story_id: "US-4-06-SUPERFICIE-CONCILIACAO-BLOQUEIOS"
task_id: "T2"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "frontend/src/pages/ativos/AtivosConciliacaoPage.tsx"
  - "frontend/src/services/ativos_recebimento.ts"
tdd_aplicavel: false
---

# TASK-2 - Vista de conciliacao planejado versus recebido

## objetivo

Implementar a vista de conciliacao: para contexto evento/categoria (filtros alinhados ao modulo Ativos), apresentar **planejado**, **recebido**, divergencia e totais **coerentes com o backend** entregue pela [US-4-03](../US-4-03-PREVALENCIA-RECEBIDO-TETO-DISTRIBUIVEL/README.md), substituindo o placeholder da T1.

## precondicoes

- [T1](./TASK-1.md) concluida (`done`).
- Endpoint(s) de leitura de saldos / conciliacao da US-4-03 disponiveis e documentados (OpenAPI ou artefato da US).
- Token via `useAuth()` como nas restantes paginas de ativos.

## orquestracao

- `depends_on`: `["T1"]`.
- `parallel_safe`: false.
- `write_scope`: pagina de conciliacao e servico HTTP dedicado; nao editar `AtivosBloqueiosRecebimentoPage.tsx` nesta task.

## arquivos_a_ler_ou_tocar

- `frontend/src/pages/ativos/AtivosConciliacaoPage.tsx`
- `frontend/src/services/ativos_recebimento.ts` *(novo; ou extensao acordada de `ativos.ts` se o gate preferir um unico modulo)*
- `frontend/src/services/ativos.ts` *(padrao `handleResponse` / `API_BASE_URL`)*
- `frontend/src/services/http.ts`
- `frontend/src/pages/AtivosList.tsx` *(padrao de filtros evento/diretoria)*

## passos_atomicos

1. Confirmar no backend paths, query params (evento_id, categoria, modo externo, etc.) e forma do JSON de resposta para totais planejado/recebido/divergencia.
2. Criar funcoes tipadas em `ativos_recebimento.ts` (ou modulo acordado) com `Authorization: Bearer`, reutilizando o mesmo tratamento de erro que `listAtivos`.
3. Em `AtivosConciliacaoPage.tsx`, implementar selecao de contexto (evento obrigatorio; categoria conforme contrato US-4-03), chamada ao servico, tabela ou cards com totais e divergencia, estados loading/skeleton e mensagem amigavel em 403/4xx como em `AtivosList`.
4. Remover texto placeholder da T1 e garantir que o titulo e a navegacao do layout pai continuam corretos.

## comandos_permitidos

- `cd frontend && npm run typecheck`
- `cd frontend && npm run lint`
- `cd frontend && npm run test -- --run` *(se adicionar testes de componente nesta task)*

## resultado_esperado

Criterio de aceite 1 da US satisfeito: ao abrir a vista de conciliacao com dados no backend, o operador ve divergencia e totais alinhados a US-4-03.

## testes_ou_validacoes_obrigatorias

- `cd frontend && npm run typecheck`.
- Teste manual: comparar totais exibidos com resposta crua do endpoint (DevTools ou cliente HTTP) para pelo menos um evento.
- Se existir suite de testes de pagina semelhante, adicionar caso minimo de render com mocks do fetch (opcional, nao obrigatorio se `tdd_aplicavel: false`).

## stop_conditions

- Parar se os endpoints US-4-03 ainda nao existirem — bloquear execucao ate backend pronto.
- Parar se o contrato JSON divergir entre documentacao e API real; escalar alinhamento antes de fixar tipos.
