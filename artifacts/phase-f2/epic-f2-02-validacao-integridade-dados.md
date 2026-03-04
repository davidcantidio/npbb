# Artifact - EPIC-F2-02 Validacao Integridade Dados

## Estado Atual

Status do artifact: `pending-execution`.

Este arquivo consolida a evidencia minima de comparacao de contagens e validacao de integridade do banco restaurado.

## Contagens Criticas

- Tabelas sob hard gate: `lead`, `evento`, `usuario`.
- Resultado atual: comparacao ainda nao executada.
- Fonte de verdade enquanto nao houver validacao: Supabase.

## Integridade e Leituras

- `backend/tests/test_lead_constraints.py`: nao executado.
- `backend/tests/test_leads_list_endpoint.py`: nao executado.
- `backend/tests/test_dashboard_leads_endpoint.py`: nao executado.

## Bloqueios

- Nao ha evidencia de equivalencia de dados.
- Nao ha evidencia de integridade relacional.
- A fase deve permanecer `hold` ate que o comparador e a suite de validacao sejam executados.
