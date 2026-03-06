---
doc_id: "EPIC-F4-02-OPENAPI-E-DOCUMENTACAO-OPERACIONAL"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-06"
---

# EPIC-F4-02 - OpenAPI e Documentacao Operacional

## Objetivo

Publicar o contrato do endpoint novo na documentacao OpenAPI e registrar orientacoes operacionais sobre cobertura BB, leitura de media/mediana e comportamento de dados parciais.

## Resultado de Negocio Mensuravel

Times de produto, QA e operacao passam a ter uma fonte oficial para integrar, validar e interpretar o dashboard sem depender de conhecimento tacito.

## Definition of Done

- O endpoint de analise etaria aparece no schema OpenAPI com query params e response model corretos.
- Existem exemplos de payload com cobertura normal e cobertura insuficiente.
- A documentacao operacional explica `sem_info`, `faixa_dominante`, `media_por_evento` e `mediana_por_evento`.
- A orientacao sobre o banner de cobertura BB instrui claramente a acao esperada do operador.

## Issues

### DLE-F4-02-001 - Publicar contrato completo no OpenAPI
Status: todo

**User story**
Como pessoa integradora de API, quero ver o endpoint etario documentado no OpenAPI para validar parametros e formato de resposta sem inspecionar codigo-fonte.

**Plano TDD**
1. `Red`: ampliar `backend/tests/test_dashboard_leads_endpoint.py` para falhar enquanto a rota nova nao estiver presente no schema gerado pela aplicacao FastAPI.
2. `Green`: ajustar annotations, `response_model` e docstrings em `backend/app/routers/dashboard_leads.py` e nos schemas associados para que o OpenAPI exponha o contrato correto.
3. `Refactor`: alinhar nomes de campos e descricoes entre schema Pydantic e texto do PRD para evitar discrepancia documental.

**Criterios de aceitacao**
- Given a aplicacao iniciada em ambiente local, When `/openapi.json` e consultado, Then existe a operacao `GET /dashboard/leads/analise-etaria`.
- Given a operacao documentada, When os schemas sao inspecionados, Then `por_evento`, `consolidado` e os query params obrigatorios aparecem tipados corretamente.

### DLE-F4-02-002 - Documentar exemplos e leitura operacional da analise
Status: todo

**User story**
Como pessoa de QA ou operacao, quero exemplos de payload e notas de interpretacao para validar rapidamente se a analise esta coerente com o PRD.

**Plano TDD**
1. `Red`: usar o proprio PRD em `PROJETOS/dashboard-leads-etaria/PRD_Dashboard_Portfolio.md` como referencia e falhar a revisao documental enquanto os exemplos de cobertura suficiente e insuficiente nao existirem.
2. `Green`: registrar exemplos de resposta e observacoes operacionais em um artefato ou documento de apoio vinculado ao epic, com foco em cobertura BB e leitura de media/mediana.
3. `Refactor`: manter os exemplos consistentes com o schema OpenAPI e com os nomes finais dos campos da API.

**Criterios de aceitacao**
- Given um payload de cobertura inferior ao threshold, When a documentacao operacional e consultada, Then ela explica por que `clientes_bb_pct` pode vir `NULL`.
- Given a secao de notas interpretativas, When a pessoa leitora consulta o documento, Then as definicoes de media e mediana reproduzem o texto do PRD sem contradicao.

## Artifact Minimo do Epico

- `artifacts/dashboard-leads-etaria/f4/epic-f4-02-openapi-e-documentacao-operacional.md`

## Dependencias

- [PRD](../PRD_Dashboard_Portfolio.md)
- [SCRUM-GOV](../../COMUM/SCRUM-GOV.md)
- [DECISION-PROTOCOL](../../COMUM/DECISION-PROTOCOL.md)
