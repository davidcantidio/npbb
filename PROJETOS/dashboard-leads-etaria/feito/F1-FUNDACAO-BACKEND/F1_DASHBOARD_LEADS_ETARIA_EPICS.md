---
doc_id: "F1_DASHBOARD_LEADS_ETARIA_EPICS.md"
version: "1.1"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
---

# Epicos - DASHBOARD-LEADS-ETARIA / F1 - FUNDACAO-BACKEND

## Objetivo da Fase

Estender o modelo de dados do Lead com os campos de cruzamento BB, formalizar os schemas Pydantic da analise etaria e expor o endpoint `GET /dashboard/leads/analise-etaria` com agregacao por evento e consolidado geral.

## Gate de Saida da Fase

O backend retorna a analise etaria consolidada e por evento com filtros de periodo e evento, cobertura BB calculada e autenticacao JWT funcionando.

## Gate de Auditoria da Fase

- estado_do_gate: `approved`
- ultima_auditoria: `F1-R02`
- veredito_atual: `go`
- relatorio_mais_recente: `./auditorias/RELATORIO-AUDITORIA-F1-R02.md`
- log_do_projeto: [AUDIT-LOG](../../AUDIT-LOG.md)
- convencao_de_relatorios: [README](./auditorias/README.md)

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F1-01 | Extensao do Modelo Lead e Migracao | Adicionar campos `is_cliente_bb` e `is_cliente_estilo`, migration Alembic e schemas atualizados. | nenhuma | done | [EPIC-F1-01-EXTENSAO-MODELO-LEAD.md](./EPIC-F1-01-EXTENSAO-MODELO-LEAD.md) |
| EPIC-F1-02 | Endpoint de Analise Etaria | Criar schemas, servico de calculo e endpoint REST da analise etaria. | EPIC-F1-01 | done | [EPIC-F1-02-ENDPOINT-ANALISE-ETARIA.md](./EPIC-F1-02-ENDPOINT-ANALISE-ETARIA.md) |

## Dependencias entre Epicos

- `EPIC-F1-01`: nenhuma
- `EPIC-F1-02`: depende de `EPIC-F1-01`

## Escopo desta Fase

### Dentro

- estender o modelo `Lead` com campos nullable de cobertura BB
- gerar e validar migration Alembic
- atualizar schemas de leitura usados por leads e dashboard
- criar schemas e servico da analise etaria
- expor endpoint JWT protegido para o dashboard
- cobrir cenarios criticos com testes backend

### Fora

- layout do dashboard no frontend
- visualizacoes, graficos e filtros na UI
- exportacao, cache obrigatorio ou permissionamento granular

## Definition of Done da Fase

- [x] campos `is_cliente_bb` e `is_cliente_estilo` existem na tabela `lead` com default `NULL`
- [x] migration Alembic aplica sem erro em banco limpo e com dados existentes
- [x] rollback da migration remove os campos sem efeito colateral
- [x] schemas `LeadListItemRead` e correlatos expostos com os novos campos
- [x] schemas `AgeAnalysisResponse`, `FaixaEtariaMetrics` e `AgeBreakdown` implementados
- [x] endpoint `GET /dashboard/leads/analise-etaria` operacional e protegido por JWT
- [x] filtros `evento_id`, `data_inicio`, `data_fim` funcionando
- [x] percentuais das faixas etarias somam 100% excluindo `sem_info`
- [x] cobertura BB calculada corretamente e threshold aplicado no payload
- [x] testes backend cobrindo faixas, cobertura e consolidado
- [x] gate de auditoria preparado para futura rodada em `auditorias/`

## Navegacao Rapida

- [Intake](../../INTAKE-DASHBOARD-LEADS-ETARIA.md)
- [PRD](../../PRD-DASHBOARD-LEADS-ETARIA.md)
- [Audit Log](../../AUDIT-LOG.md)
- [Epic F1-01](./EPIC-F1-01-EXTENSAO-MODELO-LEAD.md)
- [Epic F1-02](./EPIC-F1-02-ENDPOINT-ANALISE-ETARIA.md)
- `[[../../INTAKE-DASHBOARD-LEADS-ETARIA]]`
- `[[../../PRD-DASHBOARD-LEADS-ETARIA]]`
- `[[./EPIC-F1-01-EXTENSAO-MODELO-LEAD]]`
- `[[./EPIC-F1-02-ENDPOINT-ANALISE-ETARIA]]`
