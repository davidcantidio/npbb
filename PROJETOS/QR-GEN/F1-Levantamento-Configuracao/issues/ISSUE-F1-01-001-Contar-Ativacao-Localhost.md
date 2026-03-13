---
doc_id: "ISSUE-F1-01-001-Contar-Ativacao-Localhost.md"
version: "1.0"
status: "done"
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
- [x] Script ou query executavel
- [x] Contagem documentada
- [x] Uso documentado (como executar)

## Tasks Decupadas

- [x] T1: Criar script ou query SQL que conta `ativacao` com `landing_url` ou `url_promotor` contendo localhost/127.0.0.1
- [x] T2: Documentar saida esperada e como executar
- [x] T3: Executar em ambiente de dev/staging e registrar volume

## Arquivos Reais Envolvidos

- `backend/app/models/models.py` — modelo Ativacao
- `backend/scripts/` — local sugerido para script
- Ou documentacao inline na issue

## Artifact Minimo

- Script em `backend/scripts/count_ativacao_localhost.py` ou query documentada
- Numero de registros afetados registrado

## Como Executar

```bash
cd backend
python -m scripts.count_ativacao_localhost
```

Se o ambiente expuser apenas `python3`, use:

```bash
cd backend
python3 -m scripts.count_ativacao_localhost
```

## Saida Esperada

```text
Ativacoes com URL local persistida: <N>
Filtro: landing_url ou url_promotor contendo localhost ou 127.0.0.1.
```

## Logica da Contagem

- A contagem considera registros da tabela `ativacao` cujo `landing_url` ou `url_promotor` contenham `localhost` ou `127.0.0.1`
- A consulta conta `Ativacao.id` distintos para garantir uma linha por registro afetado
- `qr_code_url` nao entra nesta issue porque nao faz parte dos criterios de aceite definidos para F1

## Evidencia de Execucao

- Data: `2026-03-13`
- Ambiente: `dev`
- Comando executado: `cd backend && python3 -m scripts.count_ativacao_localhost`
- Volume registrado: `12` registros `ativacao` com `landing_url` ou `url_promotor` contendo `localhost` ou `127.0.0.1`

## Dependencias

- [Intake](../../INTAKE.md)
- [Epic](../EPIC-F1-01-Levantamento.md)
- [Fase](../F1_QR-GEN_EPICS.md)
- [PRD](../../PRD-QR-GEN.md)
