---
doc_id: "TASK-3.md"
user_story_id: "US-2-03-ROLLOUT-POR-EVENTO"
task_id: "T3"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - T2
parallel_safe: false
write_scope:
  - "backend/app/routers/ativos.py"
  - "backend/app/routers/ingressos.py"
tdd_aplicavel: false
---

# TASK-3 - Integrar o gate nos routers de ativos e ingressos

## objetivo

Antes de despachar qualquer ramo associado ao **novo dominio** (ou extensao
futura acordada na FEATURE-2), os endpoints relevantes de
`/ativos` e `/ingressos` devem consultar o servico de T2 com o `evento_id`
aplicavel e manter o **comportamento agregado legado** quando o gate indicar
legado, sem quebrar contratos PRD 4.0.

## precondicoes

- T2 `done` com API de resolucao estavel.
- Lista explícita de handlers que recebem ou derivam `evento_id` revisada
  *(ver passos)*.

## orquestracao

- `depends_on`: T2.
- `parallel_safe`: `false` (dois routers criticos).
- `write_scope`: apenas `ativos.py` e `ingressos.py` para integracao do gate;
  logica de negocio nova continua em servicos.

## arquivos_a_ler_ou_tocar

- `backend/app/routers/ativos.py`
- `backend/app/routers/ingressos.py`
- `backend/app/services/event_rollout_gate.py`
- `PROJETOS/ATIVOS-INGRESSOS/PRD-ATIVOS-INGRESSOS.md` *(sec. 4.0)*

## passos_atomicos

1. Inventariar endpoints que alteram ou leem estado por evento e onde o novo
   fluxo divergiria do legado; para esta US, garantir que **todos os pontos
   ja identificados na FEATURE-2** consultam o gate *(se nenhum ramo novo
   existir ainda, inserir o hook e manter unico caminho legado — sem dead code
   desnecessario, mas com ponto de extensao claro para FEATURE-3+)*.
2. Importar e invocar o servico de T2 no inicio do fluxo ou antes do branch.
3. Garantir que respostas e codigos HTTP permanecem alinhados ao baseline para
   eventos em modo legado.
4. Adicionar logging estruturado opcional (nivel debug/info) com
   `evento_id` + modo resolvido para evidenciar o criterio de aceite de suite.

## comandos_permitidos

- `cd backend && PYTHONPATH=..:. SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q`
- `ruff check` / `ruff format`

## resultado_esperado

Routers consistentes: mesmo criterio de rollout para ativos e ingressos;
comportamento legado preservado para eventos nao migrados.

## testes_ou_validacoes_obrigatorias

- Rodar a suite de testes existente dos routers tocados; corrigir falhas
  introduzidas.
- Revisao manual de um request de exemplo por endpoint alterado (legado vs
  novo) documentada no PR ou comentario de task.

## stop_conditions

- Parar se o PRD ou US exigir novo contrato HTTP sem estar escrito na US-2-03.
- Parar se `evento_id` nao estiver disponível num endpoint que precise do gate
  — escalar para clarificacao de produto.
