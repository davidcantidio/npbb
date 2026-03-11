---
doc_id: "EPIC-F1-01-EXTRAIR-NUCLEO-COMPARTILHADO"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-03"
---

# EPIC-F1-01 - Extrair Nucleo Compartilhado

## Objetivo

Migrar `column_normalize`, `segment_mapper`, `framework` e os checks de validacao para `core/leads_etl/`, preservando contratos de import, configuracao e comportamento observavel.

## Resultado de Negocio Mensuravel

O sistema passa a ter um unico nucleo reutilizavel de normalizacao e validacao de leads, reduzindo drift funcional entre o ETL em batch e a futura importacao avancada do backend.

## Definition of Done

- `core/leads_etl/transform/` e `core/leads_etl/validate/` estao definidos como destino canonico do codigo migrado.
- Imports legados de `etl.transform.*` e `etl.validate.*` continuam resolvendo sem `ModuleNotFoundError`.
- Suites ancoradas em normalizacao, segmentacao, checks e orchestrator seguem verdes apos a migracao.
- O novo nucleo compartilhado nao importa FastAPI, SQLModel ou ORM.

## Issues

### ISSUE-F1-01-01 - Migrar normalizacao de colunas para o core compartilhado
Status: todo

**User story**
Como pessoa mantenedora do pipeline, quero mover a normalizacao de colunas para `core/leads_etl/` para reutilizar a mesma regra em CLI e backend.

**Plano TDD**
1. `Red`: ampliar `tests/test_xlsx_utils.py` para expor diferencas de normalizacao entre chamadas feitas por `etl/extract/xlsx_utils.py` e o modulo atual `etl/transform/column_normalize.py` usando headers com acentos, espacos e colisoes.
2. `Green`: criar `core/leads_etl/transform/column_normalize.py`, migrar a implementacao atual e ajustar os chamadores para consumir o novo modulo mantendo o caminho legado importavel.
3. `Refactor`: reduzir `etl/transform/column_normalize.py` a um reexport compatibilizador, consolidar configuracao compartilhada e remover duplicacoes internas.

**Criterios de aceitacao**
- Given headers com acentos, espacos e colisoes, When a normalizacao roda via caminho legado e via core, Then o resultado canonico e identico.
- Given import legado de `etl.transform.column_normalize`, When a migracao termina, Then nao ha regressao de import ou comportamento em `etl/extract/xlsx_utils.py`.

### ISSUE-F1-01-02 - Migrar mapeamento de segmentos e config YAML
Status: todo

**User story**
Como pessoa responsavel pela semantica de segmentos, quero mover o mapper e seu YAML para o core compartilhado para manter a mesma classificacao em todos os fluxos.

**Plano TDD**
1. `Red`: fortalecer `tests/test_segment_mapper.py` e `tests/test_metrics_and_segments.py` para capturar qualquer mudanca de segmento ou finding ao carregar `etl/transform/segment_mapper.py` e `etl/transform/config/segment_mapping.yml`.
2. `Green`: criar `core/leads_etl/transform/segment_mapper.py`, mover a logica e a configuracao de `etl/transform/config/segment_mapping.yml` para `core/leads_etl/transform/config/segment_mapping.yml`.
3. `Refactor`: manter o loader default e os imports legados apontando para o novo local, documentando o core como fonte canonica do mapeamento.

**Criterios de aceitacao**
- Given categoria conhecida e desconhecida, When o mapper roda pelo novo core, Then segmento e finding permanecem compativeis com os testes atuais.
- Given a config movida para `core/leads_etl/transform/config`, When o loader default resolve o YAML, Then o chamador existente nao precisa mudar assinatura ou parametros.

### ISSUE-F1-01-03 - Migrar framework de validacao e checks
Status: todo

**User story**
Como pessoa responsavel por qualidade de dados, quero mover o framework de checks para `core/leads_etl/` para executar a mesma suite de validacao em qualquer entrada de leads.

**Plano TDD**
1. `Red`: ampliar `tests/test_dq_checks_schema_not_null.py`, `tests/test_dq_advanced_checks.py` e `tests/test_render_dq_report.py` para registrar qualquer divergencia de status, severidade ou evidencia em `etl/validate/framework.py`.
2. `Green`: criar `core/leads_etl/validate/framework.py` e migrar os checks usados pela suite atual para o novo pacote compartilhado.
3. `Refactor`: transformar `etl/validate/*.py` em portas de compatibilidade onde necessario, mantendo o core como implementacao real e removendo duplicacoes de contratos.

**Criterios de aceitacao**
- Given suites atuais de checks, When executadas a partir do core compartilhado, Then status, severidade e payload de evidencia permanecem compativeis com os testes existentes.
- Given imports legados de `etl.validate.*`, When a migracao conclui, Then o codigo existente continua carregando sem `ModuleNotFoundError`.

### ISSUE-F1-01-04 - Garantir reexports e isolamento de framework
Status: todo

**User story**
Como pessoa que opera a CLI e o orchestrator, quero manter os caminhos antigos importaveis durante a extracao para evitar quebra de pipeline na transicao.

**Plano TDD**
1. `Red`: usar `tests/test_etl_orchestrator_s1.py`, `tests/test_etl_orchestrator_s4.py` e `scripts/check_architecture_guards.sh` para detectar ciclos de import, regressao de interface ou dependencia proibida.
2. `Green`: implementar reexports em `etl/transform/` e `etl/validate/` que apontem para `core/leads_etl/` sem alterar a superficie publica dos modulos consumidores.
3. `Refactor`: consolidar a regra de arquitetura para bloquear imports de FastAPI, SQLModel ou ORM dentro de `core/leads_etl/`.

**Criterios de aceitacao**
- Given modulos do orchestrator e da CLI, When importados apos a extracao, Then nao ha quebra por ciclo, path antigo ou assinatura inesperada.
- Given `core/leads_etl`, When inspecionado pelos guards de arquitetura, Then ele nao importa FastAPI, SQLModel nem ORM.

## Artifact Minimo do Epico

- `artifacts/phase-f1/epic-f1-01-extrair-nucleo-compartilhado.md` com evidencias da migracao, compatibilidade de imports e status final do epico.

## Dependencias

- [PRD](../PRD-LEAD-ETL-FUSION.md)
- [GOV-SCRUM](../../../../COMUM/GOV-SCRUM.md)
- [DECISION-PROTOCOL](../DECISION-PROTOCOL.md)
