---
doc_id: "F1-AFL-EPICS"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-06"
---

# F1 Correções de UX e Integridade de Dados — Epics

## Objetivo da Fase

Corrigir problemas de usabilidade nos formulários de upload e mapeamento de leads e restaurar campos ausentes no modelo de dados, garantindo integridade e completude da informação cadastral.

## Gate de Saída da Fase

- [ ] Campo `data_envio` pré-preenchido com data atual ao abrir formulário de upload
- [ ] Dropdown de eventos exibe `nome — data_inicio_prevista` com ordenação decrescente
- [ ] Endpoint `GET /leads/referencias/eventos` retorna `data_inicio_prevista`
- [ ] Modelo `Lead` possui os 8 campos restaurados (`sobrenome`, `rg`, `genero`, `logradouro`, `numero`, `complemento`, `bairro`, `cep`)
- [ ] Migration Alembic aplicável sem erro em banco com dados existentes
- [ ] Schemas de leitura e tipo `LeadListItem` no frontend atualizados
- [ ] Importação de CSV existente não quebra (retrocompatibilidade)
- [ ] CI verde sem regressão

## Epics da Fase

| Epic ID | Nome | Objetivo | Status | Documento |
|---------|------|----------|--------|-----------|
| `EPIC-F1-01` | Ajustes de UX no Upload e Dropdown | Melhorar usabilidade do formulário de upload (data padrão) e do dropdown de eventos (exibir data). | 🔲 | [EPIC-F1-01-AJUSTES-UX-UPLOAD-E-DROPDOWN.md](./EPIC-F1-01-AJUSTES-UX-UPLOAD-E-DROPDOWN.md) |
| `EPIC-F1-02` | Extensão do Modelo Lead — Campos Ausentes | Restaurar campos de dados pessoais e endereço ao modelo Lead com migration e schemas. | 🔲 | [EPIC-F1-02-EXTENSAO-MODELO-LEAD-CAMPOS-AUSENTES.md](./EPIC-F1-02-EXTENSAO-MODELO-LEAD-CAMPOS-AUSENTES.md) |

## Escopo desta Entrega

**Incluso:**
- Pré-preenchimento de `data_envio` no formulário de upload (PRD 3.1)
- Exibição de `data_inicio_prevista` no dropdown de eventos e ordenação decrescente (PRD 3.2)
- Adição dos 8 campos ausentes ao modelo Lead, migration e schemas (PRD 3.3)

**Fora de escopo:**
- Criação rápida de evento (F2)
- Exportação de leads Gold (F3)
- Índices compostos para performance de dashboard (avaliar após medição)
