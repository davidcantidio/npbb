---
doc_id: "TASK-1.md"
us_id: "US-1-01-INGESTAO-E-MAPEAMENTO-INICIAL"
task_id: "T1"
version: "1.1"
status: "done"
owner: "PM"
last_updated: "2026-04-09"
tdd_aplicavel: true
---

# T1 - Estruturar lote Bronze e mapeamento Silver inicial

## objetivo

Definir e implementar a base minima da feature piloto: criacao do lote Bronze,
registro de metadados e persistencia do mapeamento inicial para Silver.

## precondicoes

- intake e PRD do projeto ativos
- feature e user story piloto criadas
- contexto tecnico do fluxo atual de ingestao localizado no backend e frontend

## arquivos_a_ler_ou_tocar

- `PROJETOS/NPBB/INTAKE-NPBB.md`
- `PROJETOS/NPBB/PRD-NPBB.md`
- `PROJETOS/NPBB/features/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD.md`
- `PROJETOS/NPBB/features/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD/user-stories/US-1-01-INGESTAO-E-MAPEAMENTO-INICIAL/README.md`
- `backend/`
- `frontend/`
- `lead_pipeline/`

## passos_atomicos

1. localizar o fluxo atual de upload/importacao de leads no backend e frontend
2. mapear os pontos minimos para persistir um lote Bronze com metadados
3. definir o estado minimo do mapeamento Silver para o lote piloto
4. implementar testes do caminho feliz e dos campos obrigatorios
5. atualizar handoff de revisao com evidencias e arquivos alterados

## comandos_permitidos

- `rg -n "lead_batches|leads_silver|upload|importacao|silver|bronze|gold" backend frontend lead_pipeline`
- `pytest -q tests/test_criar_projeto.py tests/test_fabrica_boundary.py`
- `git status --short`

## resultado_esperado

Lote Bronze persistido, mapeamento Silver inicial definido e a primeira US
pronta para revisao no formato atual do framework.

## testes_ou_validacoes_obrigatorias

- cobrir criacao do lote com campos obrigatorios
- cobrir falha quando metadados obrigatorios estiverem ausentes
- validar que o projeto nao referencia wrappers legados

## stop_conditions

- parar se o modelo de dados atual nao permitir rastreabilidade minima do lote
- parar se a implementacao exigir reintroduzir artefatos do paradigma legado
