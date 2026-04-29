---
doc_id: "EPIC-F2-01-QUERY-SERVICE-ANALISE-ETARIA"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-06"
---

# EPIC-F2-01 - Query Service Analise Etaria

## Objetivo

Construir a camada de agregacao que calcula faixas etarias por evento, consolidado geral, cobertura BB, faixa dominante, Top 3, media e mediana usando os dados ja ingeridos no backend.

## Resultado de Negocio Mensuravel

O dashboard deixa de depender de planilhas externas para produzir leitura etaria consolidada e passa a oferecer indicadores reproduziveis a partir do banco do produto.

## Definition of Done

- Existe um servico dedicado no backend para a analise etaria sem logica de agregacao espalhada pelo router.
- O servico trata `sem_info` fora dos percentuais e calcula percentuais sobre a base com idade conhecida.
- O consolidado geral calcula corretamente `top_eventos`, `concentracao_top3_pct`, `media_por_evento` e `mediana_por_evento`.
- A faixa dominante por evento e derivada do maior volume entre `18-25`, `26-40` e `fora_18_40`.

## Issues

### DLE-F2-01-001 - Calcular faixas etarias por evento
Status: todo

**User story**
Como pessoa usuaria do dashboard, quero ver as faixas 18-25, 26-40, fora de 18-40 e sem informacao por evento para entender rapidamente o perfil etario de cada carteira.

**Plano TDD**
1. `Red`: ampliar `backend/tests/test_dashboard_leads_report_endpoint.py` para falhar quando um conjunto de leads com `data_nascimento` conhecido e nulo nao resultar nas quatro categorias previstas.
2. `Green`: criar um servico dedicado, por exemplo em `backend/app/services/`, reutilizando joins ja presentes em `backend/app/routers/dashboard_leads.py` para agrupar por evento e calcular as faixas.
3. `Refactor`: extrair helpers de calculo de idade e percentual para manter a consulta legivel e reutilizavel no consolidado.

**Criterios de aceitacao**
- Given um evento com leads em cada faixa e leads sem `data_nascimento`, When o servico monta `por_evento`, Then os volumes aparecem nas chaves corretas e `sem_info` fica fora dos percentuais.
- Given um evento sem qualquer lead com idade conhecida, When o servico calcula percentuais, Then `18-25`, `26-40` e `fora_18_40` retornam `0` sem divisao por zero.

### DLE-F2-01-002 - Calcular consolidado geral e rankings do portfolio
Status: todo

**User story**
Como pessoa gestora do portfolio, quero um consolidado geral com Top 3, media e mediana para comparar o tamanho tipico dos eventos e a concentracao da base.

**Plano TDD**
1. `Red`: ampliar `backend/tests/test_dashboard_leads_endpoint.py` para falhar quando o consolidado nao refletir soma total, media, mediana e ranking dos tres maiores eventos.
2. `Green`: implementar no servico analitico a agregacao global e o ordenamento de `top_eventos` por `base_leads`.
3. `Refactor`: concentrar as funcoes de estatistica descritiva no mesmo modulo do servico para evitar duplicacao com o relatorio legado.

**Criterios de aceitacao**
- Given tres ou mais eventos com volumes distintos, When o consolidado e calculado, Then `top_eventos` vem ordenado do maior para o menor por `base_leads`.
- Given volumes ordenados, When `media_por_evento` e `mediana_por_evento` sao gerados, Then os valores seguem exatamente as definicoes do PRD.

### DLE-F2-01-003 - Aplicar cobertura BB e nullability das metricas
Status: todo

**User story**
Como pessoa usuaria do dashboard, quero que a taxa de clientes BB respeite a cobertura real do cruzamento para nao interpretar dados ausentes como nao clientes.

**Plano TDD**
1. `Red`: ampliar `backend/tests/test_dashboard_leads_report_endpoint.py` para falhar quando leads com `is_cliente_bb=None` forem contados como nao clientes ou quando a cobertura nao for calculada.
2. `Green`: implementar no servico a regra de cobertura com threshold default de 80%, retornando `clientes_bb_volume` e `clientes_bb_pct` como `NULL` abaixo do limite aplicavel.
3. `Refactor`: isolar a politica de threshold e mensagens para reaproveitamento no endpoint e no frontend.

**Criterios de aceitacao**
- Given um evento com cobertura abaixo do threshold, When o servico monta a resposta, Then `clientes_bb_volume` e `clientes_bb_pct` retornam `NULL` e `cobertura_bb_pct` informa a cobertura real.
- Given um evento com cobertura suficiente, When o servico calcula a resposta, Then `clientes_bb_pct` usa apenas os valores explicitamente conhecidos sem inferir `NULL` como `False`.

## Artifact Minimo do Epico

- `artifacts/dashboard-leads-etaria/f2/epic-f2-01-query-service-analise-etaria.md`

## Dependencias

- [PRD](../PRD_Dashboard_Portfolio.md)
- [SCRUM-GOV](../../COMUM/SCRUM-GOV.md)
- [DECISION-PROTOCOL](../../COMUM/DECISION-PROTOCOL.md)
