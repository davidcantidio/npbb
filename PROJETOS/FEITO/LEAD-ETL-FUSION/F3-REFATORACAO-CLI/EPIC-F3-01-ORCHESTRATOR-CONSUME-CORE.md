---
doc_id: "EPIC-F3-01-ORCHESTRATOR-CONSUME-CORE"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-03"
---

# EPIC-F3-01 - Orchestrator Consume Core

## Objetivo

Atualizar `etl/orchestrator/s1_core.py` ate `etl/orchestrator/s4_core.py` para consumir `column_normalize`, `segment_mapper` e o framework de validacao a partir de `core/leads_etl/`, sem mudar a interface publica da CLI.

## Resultado de Negocio Mensuravel

O pipeline em batch passa a compartilhar o mesmo nucleo logico que sera usado no backend, reduzindo manutencao paralela e risco de comportamento inconsistente entre execucoes humanas e HTTP.

## Definition of Done

- Os modulos `s1_core.py` ate `s4_core.py` deixam de depender da implementacao real em `etl/transform/` e `etl/validate/`.
- `cli_extract.py` e `cli_spec.py` continuam com a mesma interface de linha de comando.
- Modulos de observabilidade e testes de orchestrator continuam funcionando com os novos imports.
- As suites de regressao do ETL permanecem verdes apos a troca do nucleo.

## Issues

### ISSUE-F3-01-01 - Atualizar s1_core.py e s2_core.py para consumir o core
Status: todo

**User story**
Como pessoa que opera os primeiros estagios do ETL, quero que `s1_core.py` e `s2_core.py` consumam o novo core para iniciar a migracao sem alterar a experiencia da CLI.

**Plano TDD**
1. `Red`: ampliar `tests/test_etl_orchestrator_s1.py` e `tests/test_etl_orchestrator_s2.py` para falhar quando `etl/orchestrator/s1_core.py` e `etl/orchestrator/s2_core.py` ainda dependerem da implementacao real fora de `core/leads_etl/`.
2. `Green`: ajustar `etl/orchestrator/s1_core.py` e `etl/orchestrator/s2_core.py` para importar `column_normalize`, `segment_mapper` e validacao a partir do core compartilhado.
3. `Refactor`: consolidar helpers e imports compartilhados dos dois estagios para que a padronizacao de acesso ao core fique explicita e repetivel.

**Criterios de aceitacao**
- Given etapas s1 e s2, When executadas, Then importam `column_normalize`, `segment_mapper` e validacao do novo core.
- Given fixtures existentes do orchestrator, When a suite roda, Then nao ha alteracao de interface, assinatura ou comportamento observavel.

### ISSUE-F3-01-02 - Atualizar s3_core.py e s4_core.py para consumir o core
Status: todo

**User story**
Como pessoa que mantem os estagios finais do ETL, quero que `s3_core.py` e `s4_core.py` passem a usar o mesmo nucleo compartilhado para eliminar a segunda metade da duplicacao estrutural.

**Plano TDD**
1. `Red`: ampliar `tests/test_etl_orchestrator_s3.py` e `tests/test_etl_orchestrator_s4.py` para detectar qualquer dependencia restante de implementacao real em caminhos legados.
2. `Green`: atualizar `etl/orchestrator/s3_core.py` e `etl/orchestrator/s4_core.py` para consumir o core compartilhado, preservando a semantica dos checks e relatorios.
3. `Refactor`: harmonizar os quatro estagios do orchestrator para que todos sigam o mesmo padrao de import e montagem de pipeline.

**Criterios de aceitacao**
- Given etapas s3 e s4, When executadas, Then o consumo do nucleo compartilhado e consistente com s1 e s2.
- Given checks e relatorios existentes, When processados apos a troca, Then as saidas continuam equivalentes para os testes atuais.

### ISSUE-F3-01-03 - Proteger CLI e observability sem mudar interface publica
Status: todo

**User story**
Como pessoa que roda a CLI em producao ou analise, quero preservar flags, fluxo de observabilidade e pontos de entrada para que a refatoracao seja invisivel na operacao.

**Plano TDD**
1. `Red`: ampliar `tests/test_etl_extract_ai_s1.py`, `tests/test_etl_extract_ai_s4.py` e testes de observabilidade para falhar diante de qualquer mudanca de interface ou import em `etl/cli_extract.py` e `etl/cli_spec.py`.
2. `Green`: adaptar os pontos de entrada da CLI e os modulos `*_observability.py` para consumirem o core sem alterar flags, nomes de comando ou fluxo de log.
3. `Refactor`: centralizar imports compartilhados e remover acoplamentos acidentais do orchestrator com paths internos antigos.

**Criterios de aceitacao**
- Given usuarios atuais da CLI, When executam os comandos existentes, Then flags, assinaturas e comportamento externo continuam inalterados.
- Given modulos `*_observability.py`, When o pipeline carrega apos a refatoracao, Then nao ha regressao de import nem de telemetria esperada.

## Artifact Minimo do Epico

- `artifacts/phase-f3/epic-f3-01-orchestrator-consume-core.md` com evidencias de import compartilhado, regressao da CLI e status final do orchestrator.

## Dependencias

- [PRD](../PRD-LEAD-ETL-FUSION.md)
- [GOV-SCRUM](../../../../COMUM/GOV-SCRUM.md)
- [DECISION-PROTOCOL](../DECISION-PROTOCOL.md)
