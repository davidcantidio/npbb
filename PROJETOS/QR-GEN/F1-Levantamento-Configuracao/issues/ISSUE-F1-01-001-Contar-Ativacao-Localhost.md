---
doc_id: "ISSUE-F1-01-001-Contar-Ativacao-Localhost.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F1-01-001 - Contar Ativacao Localhost

## User Story

Como PM ou DevOps, quero um script ou query para contar registros `ativacao` com URL local persistida, para planejar a migracao e dimensionar o esforco.

## Contexto Tecnico

A tabela `ativacao` possui colunas `landing_url`, `qr_code_url` e `url_promotor`. Registros criados em ambiente local podem conter `localhost` ou `127.0.0.1` nessas colunas. O PRD exige levantamento do volume antes da migracao.

## Plano TDD

- Red: N/A (script de consulta, sem logica de negocio complexa)
- Green: Script/query retorna contagem correta
- Refactor: Documentar uso e saida esperada

## Criterios de Aceitacao

- Given a tabela `ativacao` com registros variados, When executo o script ou query, Then obtenho a contagem de registros onde `landing_url` ou `url_promotor` contem `localhost` ou `127.0.0.1`
- Given o resultado, When documento na issue ou em artefato, Then o volume fica registrado para planejamento da F2

## Definition of Done da Issue
- [ ] Script ou query executavel
- [ ] Contagem documentada
- [ ] Uso documentado (como executar)

## Tasks Decupadas

- [ ] T1: Criar script ou query SQL que conta `ativacao` com `landing_url` ou `url_promotor` contendo localhost/127.0.0.1
- [ ] T2: Documentar saida esperada e como executar
- [ ] T3: Executar em ambiente de dev/staging e registrar volume

## Arquivos Reais Envolvidos

- `backend/app/models/models.py` — modelo Ativacao
- `backend/scripts/` — local sugerido para script
- Ou documentacao inline na issue

## Artifact Minimo

- Script em `backend/scripts/count_ativacao_localhost.py` ou query documentada
- Numero de registros afetados registrado

## Dependencias

- [Intake](../../INTAKE.md)
- [Epic](../EPIC-F1-01-Levantamento.md)
- [Fase](../F1_QR-GEN_EPICS.md)
- [PRD](../../PRD-QR-GEN.md)
