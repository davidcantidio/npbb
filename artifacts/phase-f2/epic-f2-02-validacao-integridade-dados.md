# Artifact - EPIC-F2-02 Validacao Integridade Dados

## Estado Atual

Status do artifact: `partial`.

Este arquivo consolida a evidencia minima de comparacao de contagens e validacao de integridade do banco restaurado.

## Contagens Criticas

- Tabelas sob hard gate: `lead`, `evento`, `usuario`.
- Resultado atual: comparacao entre Supabase e destino local ainda nao executada (requer acesso a ambos os bancos).
- Fonte de verdade enquanto nao houver validacao: Supabase.

## Integridade e Leituras

- `backend/tests/test_lead_constraints.py`: executado em 2026-04-13, resultado: passed.
- `backend/tests/test_leads_list_endpoint.py`: executado em 2026-04-13, resultado: passed.
- `backend/tests/test_dashboard_leads_endpoint.py`: executado em 2026-04-13, resultado: passed.

Total: 17 passed (execucao local com SQLite em modo TESTING).

## Bloqueios

- Nao ha evidencia de equivalencia de dados entre Supabase e destino local (requer janela de migracao).
- Suites de integridade relacional e leituras essenciais estao verdes em ambiente de teste.
- A fase permanece `hold` para a comparacao de contagens em banco real.
