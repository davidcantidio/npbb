---
doc_id: "ISSUE-F2-02-001-Validacao-Zero-Localhost.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F2-02-001 - Validacao Zero Localhost

## User Story

Como DevOps ou QA, quero um teste de validacao que garanta zero registros com localhost apos a migracao, para confirmar que a metrica de sucesso foi atingida.

## Contexto Tecnico

Apos a migracao da F2, a metrica de sucesso e: zero QR codes com URL de localhost persistidos no banco. O teste deve consultar a tabela `ativacao` e falhar se existir qualquer registro com `landing_url` ou `url_promotor` contendo localhost ou 127.0.0.1.

## Plano TDD

- Red: Teste falha quando existem registros com localhost
- Green: Teste passa quando nao existem registros com localhost
- Refactor: Integrar em CI se aplicavel

## Criterios de Aceitacao

- Given o banco apos migracao, When executo o teste de validacao, Then o teste passa (zero registros com localhost)
- Given o banco com registros com localhost, When executo o teste, Then o teste falha com mensagem clara
- Given ambiente de staging/producao, When a migracao for executada, Then este teste pode ser rodado para validar

## Definition of Done da Issue
- [ ] Teste de validacao criado e passando
- [ ] Teste falha corretamente quando ha registros incorretos
- [ ] Documentado como passo pos-migracao

## Tasks Decupadas

- [ ] T1: Criar funcao ou script que consulta ativacao com landing_url ou url_promotor contendo localhost/127.0.0.1
- [ ] T2: Se count > 0, levantar AssertionError ou exit(1) com mensagem descritiva
- [ ] T3: Integrar em pytest ou script standalone executavel
- [ ] T4: Documentar no README ou docs como executar apos migracao

## Arquivos Reais Envolvidos

- `backend/tests/test_ativacao_url_validation.py` ou similar
- `backend/scripts/validate_no_localhost_urls.py` (se standalone)
- `backend/app/models/models.py` — Ativacao

## Artifact Minimo

- Teste ou script de validacao executavel
- Documentacao de uso

## Dependencias

- [Intake](../../INTAKE.md)
- [Epic](../EPIC-F2-02-Validacao.md)
- [Fase](../F2_QR-GEN_EPICS.md)
- [PRD](../../PRD-QR-GEN.md)
- [EPIC-F2-01](../EPIC-F2-01-Migracao.md) — migracao executada
