# Épicos — Dashboard Leads Etária / F1 — Fundação Backend
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** DASHBOARD-LEADS-ETARIA | **fase:** F1
**prd:** ../PRD_Dashboard_Portfolio.md
**status:** aprovado

---
## Objetivo da Fase
Estender o modelo de dados do Lead com os campos de cruzamento BB (`is_cliente_bb`,
`is_cliente_estilo`), criar os schemas Pydantic da análise etária e implementar o
endpoint `GET /api/v1/dashboard/leads/analise-etaria` com lógica de cálculo de faixas
etárias, cobertura de dados BB e agregação consolidada.

Ao final da fase, o backend já deve servir os dados completos de análise etária por
evento e consolidada, com filtros de período e evento, prontos para consumo pelo
frontend.

## Épicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F1-01 | Extensão do Modelo Lead e Migração | Adicionar campos `is_cliente_bb` e `is_cliente_estilo` ao modelo Lead com migration Alembic e schemas atualizados. | nenhuma | 🔲 | `EPIC-F1-01-EXTENSAO-MODELO-LEAD.md` |
| EPIC-F1-02 | Endpoint de Análise Etária | Criar schemas de resposta, lógica de query com faixas etárias e endpoint REST da análise etária. | EPIC-F1-01 | 🔲 | `EPIC-F1-02-ENDPOINT-ANALISE-ETARIA.md` |

## Dependências entre Épicos
`EPIC-F1-01` → `EPIC-F1-02`

## Definition of Done da Fase
- [ ] Campos `is_cliente_bb` e `is_cliente_estilo` existem na tabela `lead` com default `NULL`
- [ ] Migration Alembic aplica sem erro em banco limpo e com dados existentes
- [ ] Rollback da migration remove os campos sem efeito colateral
- [ ] Schemas `LeadListItemRead` atualizados com novos campos
- [ ] Schemas `AgeAnalysisResponse`, `FaixaEtariaMetrics`, `AgeBreakdown` implementados
- [ ] Endpoint `GET /api/v1/dashboard/leads/analise-etaria` operacional e protegido por JWT
- [ ] Filtros `evento_id`, `data_inicio`, `data_fim` funcionando
- [ ] Percentuais de faixas etárias somam 100% (excluindo leads sem `data_nascimento`)
- [ ] Cobertura BB calculada corretamente e threshold aplicado
- [ ] Testes unitários cobrindo cenários de faixas, cobertura e consolidado

## Notas e Restrições
- Campos `is_cliente_bb` e `is_cliente_estilo` são nullable — retrocompatibilidade obrigatória
- Faixa etária calculada na query, não persistida
- Leads com `data_nascimento NULL` contabilizados como "sem informação" e excluídos dos percentuais
- Caching opcional (TTL 5 min) pode ser avaliado mas não é obrigatório nesta fase
