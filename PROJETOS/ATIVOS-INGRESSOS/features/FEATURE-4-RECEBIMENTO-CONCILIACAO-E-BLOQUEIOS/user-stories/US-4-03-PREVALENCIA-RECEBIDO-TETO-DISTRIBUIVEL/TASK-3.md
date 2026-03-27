---
doc_id: "TASK-3.md"
user_story_id: "US-4-03-PREVALENCIA-RECEBIDO-TETO-DISTRIBUIVEL"
task_id: "T3"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "backend/app/routers/ativos.py"
  - "backend/app/schemas/ativos.py"
  - "backend/tests/test_ativos_endpoints.py"
tdd_aplicavel: false
---

# TASK-3 - API de leitura da divergencia planejado vs recebido

## objetivo

Expor via API (preferencialmente extensao do router de ativos ja alinhado a operacao BB e FEATURE-3) uma leitura onde **operador ou integracao** obtenha **planejado**, **recebido confirmado** e **delta** de forma estavel e auditavel, usando a mesma regra numerica de T1, cumprindo o segundo criterio Given/When/Then da US.

## precondicoes

- T1 `done`.
- Se T2 alterou convencoes compartilhadas (helpers, imports) em `ingressos.py`, sincronizar antes desta task para evitar duplicacao; **nao** duplicar logica de negocio fora do servico de T1.

## orquestracao

- `depends_on`: `T1` *(T2 nao e predecessora logica; execute apos T2 se houver conflito de merge no mesmo sprint)*.
- `parallel_safe`: `false`.
- `write_scope`: conforme frontmatter; se o projeto padronizar o recurso sob `ingressos.py` em vez de `ativos.py`, ajustar apenas `write_scope` e ficheiros tocados mantendo o objetivo da US.

## arquivos_a_ler_ou_tocar

- `backend/app/services/ativos_ingressos_saldo.py`
- `backend/app/routers/ativos.py`
- `backend/app/schemas/ativos.py`
- `backend/tests/test_ativos_endpoints.py`
- `PROJETOS/ATIVOS-INGRESSOS/PRD-ATIVOS-INGRESSOS.md` *(sec. 2.4 — contexto apenas)*

## passos_atomicos

1. Definir schema Pydantic de resposta com campos explicitos `planejado`, `recebido_confirmado`, `delta` (e identificadores de eixo: evento, diretoria, categoria, lote se aplicavel).
2. Implementar endpoint GET (ou sub-recurso) autenticado com RBAC coerente ao modulo de ativos.
3. Agregar dados do banco conforme modelo US-4-01/4-02 e passar pelo servico de T1 para garantir consistencia do delta com o teto usado em distribuicao.
4. Tratar ausencia de recebimento com valores explicitos (ex.: recebido zero) de forma auditavel.
5. Adicionar testes HTTP em `test_ativos_endpoints.py` cobrindo resposta 200 com os tres campos e caso 4xx para recurso fora de escopo.

## comandos_permitidos

- `cd backend && PYTHONPATH=..:. SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_ativos_endpoints.py`
- `cd backend && ruff check app/routers/ativos.py app/schemas/ativos.py`

## resultado_esperado

- Contrato JSON documentado e testado para consulta de divergencia.
- Nenhuma escrita de negocio neste endpoint; somente leitura.

## testes_ou_validacoes_obrigatorias

- Testes HTTP green para payload com planejado, recebido e delta.
- Verificacao de que o delta coincide com o calculo unitario de T1 para um fixture fixo.

## stop_conditions

- Parar com `BLOQUEADO` se RBAC ou visibilidade por agencia nao estiver definida para o novo recurso.
- Parar se T1 nao exportar uma API reutilizavel para montar a resposta sem copiar formulas.
