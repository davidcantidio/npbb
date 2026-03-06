---
doc_id: "F3-AFL-EPICS"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-06"
---

# F3 Exportação de Leads Gold — Epics

## Objetivo da Fase

Implementar a funcionalidade de exportação de leads em estágio Gold a partir do Dashboard de Leads, com filtro por evento e suporte a formatos `.xlsx` e `.csv`, permitindo que o operador extraia dados tratados para uso externo.

## Gate de Saída da Fase

- [ ] Endpoint `GET /leads/export/gold` operacional com filtro por `evento_id` e parâmetro `formato`
- [ ] Arquivo gerado contém todas as colunas definidas no PRD (seção 4.7)
- [ ] Nome do arquivo segue padrão `leads_ouro_[evento]_YYYY-MM-DD.[ext]`
- [ ] CSV usa separador `;` e encoding UTF-8 com BOM
- [ ] Botão "Exportar Leads Ouro" visível no `DashboardLeads.tsx`
- [ ] Modal de exportação com seleção de evento e formato funcional
- [ ] Download automático via Blob URL
- [ ] HTTP 204 com toast informativo quando nenhum lead Gold é encontrado
- [ ] CI verde sem regressão

## Epics da Fase

| Epic ID | Nome | Objetivo | Status | Documento |
|---------|------|----------|--------|-----------|
| `EPIC-F3-01` | Endpoint e Serviço de Exportação Gold | Criar endpoint backend de exportação com geração de .xlsx/.csv e filtros. | 🔲 | [EPIC-F3-01-ENDPOINT-EXPORTACAO-GOLD.md](./EPIC-F3-01-ENDPOINT-EXPORTACAO-GOLD.md) |
| `EPIC-F3-02` | Interface de Exportação no Dashboard | Implementar botão, modal e download no DashboardLeads. | 🔲 | [EPIC-F3-02-UI-EXPORTACAO-DASHBOARD.md](./EPIC-F3-02-UI-EXPORTACAO-DASHBOARD.md) |

## Escopo desta Entrega

**Incluso:**
- Novo endpoint `GET /leads/export/gold` com filtro por evento e formato (PRD 4.5)
- Geração de arquivo .xlsx e .csv com colunas definidas no PRD (PRD 4.7)
- Nomenclatura de arquivo conforme PRD (PRD 4.8)
- Regras de negócio: apenas `stage=gold`, `pipeline_status IN (pass, pass_with_warnings)` (PRD 4.9)
- Serviço frontend `exportLeadsGold()` com download via Blob (PRD 4.6)
- Botão e modal de exportação no `DashboardLeads.tsx` (PRD 4.3, 4.4)

**Fora de escopo:**
- Exportação de leads em outros estágios (`bronze`, `silver`)
- Envio do arquivo por e-mail
- Agendamento automático de exportações
- Integração com ferramentas externas (Google Sheets, CRMs)
- Edição em massa de leads via exportação/reimportação

**Dependência opcional:**
- Campos extras de exportação (`sobrenome`, `rg`, `genero`, endereço) dependem de EPIC-F1-02. Se F1 não estiver concluída, esses campos são exportados como vazio.
