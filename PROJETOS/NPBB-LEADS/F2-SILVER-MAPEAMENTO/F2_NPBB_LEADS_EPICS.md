# Épicos — NPBB-LEADS / F2 — Silver: Mapeamento
**version:** 1.0.0 | **last_updated:** 2026-03-03
**projeto:** NPBB-LEADS | **fase:** F2

## Objetivo da Fase
Permitir que o operador defina o evento de referência, mapeie as colunas do arquivo
para os campos canônicos do banco (com sugestão automática baseada em HEADER_SYNONYMS
e aliases salvos), persista os dados brutos mapeados em `leads_silver` e salve os
aliases de coluna para reuso futuro.

## Épicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F2-01 | Mapeamento e Persistência Silver | Backend de mapeamento + persistência silver + aliases | F1 concluída | 🔲 | `EPIC-F2-01-MAPEAMENTO-E-PERSISTENCIA-SILVER.md` |

## Definition of Done da Fase
- [ ] Endpoint de preview de colunas com sugestão automática
- [ ] Operador confirma mapeamento e vincula evento
- [ ] Dados persistidos em `leads_silver` com batch_id e row_index
- [ ] Aliases salvos em `lead_column_aliases`
- [ ] Stage do lote atualizado para `silver`
- [ ] CI verde