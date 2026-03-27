---
doc_id: "TASK-3.md"
user_story_id: "US-4-06-SUPERFICIE-CONCILIACAO-BLOQUEIOS"
task_id: "T3"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T2"
parallel_safe: false
write_scope:
  - "frontend/src/pages/ativos/AtivosBloqueiosRecebimentoPage.tsx"
  - "frontend/src/services/ativos_recebimento.ts"
tdd_aplicavel: false
---

# TASK-3 - Vista de itens bloqueados por recebimento

## objetivo

Implementar lista e detalhe (ou painel) dos itens em estado `bloqueado_por_recebimento`, com **motivo do bloqueio visivel** e possibilidade de **atualizar** a vista apos novo recebimento (refetch ou invalidacao), alinhado a [US-4-04](../US-4-04-BLOQUEIO-POR-RECEBIMENTO/README.md).

## precondicoes

- [T2](./TASK-2.md) concluida (`done`) para manter ordem e reutilizar padroes de servico HTTP na mesma US.
- Endpoint(s) de listagem/consulta de bloqueios da US-4-04 disponiveis e documentados.

## orquestracao

- `depends_on`: `["T2"]`.
- `parallel_safe`: false.
- `write_scope`: pagina de bloqueios e extensoes no mesmo servico `ativos_recebimento.ts`; evitar conflito com T2 coordenando commits ou fazendo alteracoes incrementais no servico apos T2 mergeada.

## arquivos_a_ler_ou_tocar

- `frontend/src/pages/ativos/AtivosBloqueiosRecebimentoPage.tsx`
- `frontend/src/services/ativos_recebimento.ts`
- `frontend/src/pages/ativos/AtivosConciliacaoPage.tsx` *(consistencia de filtros e UX)*
- Artefato / OpenAPI da US-4-04

## passos_atomicos

1. Mapear contrato de listagem (paginacao, filtros por evento/categoria) e campos que explicam o motivo do bloqueio.
2. Adicionar funcoes no servico HTTP para listar e, se aplicavel, obter detalhe de um bloqueio.
3. Implementar UI: tabela ou lista com colunas claras (ex.: entidade afetada, categoria, motivo, data); acao **Atualizar** que refaz o fetch; opcional detalhe em drawer/dialog.
4. Garantir que, apos simulacao ou registo de novo recebimento (via API ou T4), o utilizador pode refrescar e ver estado atualizado.
5. Remover placeholder da T1.

## comandos_permitidos

- `cd frontend && npm run typecheck`
- `cd frontend && npm run lint`
- `cd frontend && npm run test -- --run` *(se testes de componente forem adicionados)*

## resultado_esperado

Criterio de aceite 2 da US satisfeito: motivo visivel; dados atualizaveis apos novo recebimento.

## testes_ou_validacoes_obrigatorias

- `cd frontend && npm run typecheck`.
- Teste manual: com dados de teste em `bloqueado_por_recebimento`, confirmar motivo exibido; apos operacao de recebimento, refetch e validar mudanca de estado ou mensagem esperada.

## stop_conditions

- Parar se a API US-4-04 nao expuser motivo legivel — exigir alinhamento com backend antes de inventar copy.
- Parar se T2 ainda nao tiver fechado alteracoes pendentes em `ativos_recebimento.ts` que conflitem com esta task.
