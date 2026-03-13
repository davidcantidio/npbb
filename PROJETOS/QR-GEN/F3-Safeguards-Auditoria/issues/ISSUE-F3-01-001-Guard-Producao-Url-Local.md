---
doc_id: "ISSUE-F3-01-001-Guard-Producao-Url-Local.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F3-01-001 - Guard Producao URL Local

## User Story

Como desenvolvedor ou DevOps, quero um guard que detecte quando a URL calculada para `ativacao` contiver host local em ambiente de producao, para evitar regressao e falhas silenciosas.

## Contexto Tecnico

O servico `hydrate_ativacao_public_urls` persiste `landing_url` e `qr_code_url` na tabela `ativacao`. Em producao, se `get_public_app_base_url()` retornar localhost (por configuracao ausente), os registros ficarao incorretos. O guard deve levantar erro ou warning quando, em producao, a URL calculada contiver `localhost` ou `127.0.0.1`. Ambiente de producao pode ser detectado por `ENVIRONMENT=production` ou `PUBLIC_APP_BASE_URL` contendo dominio de producao.

## Plano TDD

- Red: Teste que em producao (monkeypatch), URL local gera erro ou warning
- Green: Guard implementado; em dev local, comportamento preservado
- Refactor: Extrair funcao de deteccao de ambiente se necessario

## Criterios de Aceitacao

- Given ambiente de producao (ENVIRONMENT=production ou equivalente), When a URL calculada contiver localhost ou 127.0.0.1, Then o guard levanta erro ou warning e impede ou sinaliza a persistencia
- Given ambiente de desenvolvimento, When a URL for localhost, Then o fluxo continua normal (sem guard bloqueante)
- Given o guard implementado, When executo testes com monkeypatch de env, Then o cenario producao vs dev e coberto

## Definition of Done da Issue
- [ ] Guard implementado em hydrate_ativacao_public_urls ou ponto adequado
- [ ] Teste automatizado cobrindo producao (erro/warning) e dev (sem bloqueio)
- [ ] Documentacao do comportamento

## Tasks Decupadas

- [ ] T1: Implementar funcao ou logica para detectar ambiente de producao
- [ ] T2: Adicionar guard que verifica se URL calculada contem localhost/127.0.0.1 em producao
- [ ] T3: Em producao com URL local: levantar ValueError ou logging.warning (conforme decisao)
- [ ] T4: Adicionar teste com monkeypatch para cenario producao vs dev
- [ ] T5: Garantir que fluxo de dev local continua funcional

## Arquivos Reais Envolvidos

- `backend/app/services/landing_pages.py` — hydrate_ativacao_public_urls
- `backend/app/utils/urls.py` — get_public_app_base_url, build_ativacao_public_urls
- `backend/tests/test_qr_code_service.py` ou novo arquivo de teste

## Artifact Minimo

- Guard em codigo
- Teste passando

## Dependencias

- [Intake](../../INTAKE.md)
- [Epic](../EPIC-F3-01-Safeguards.md)
- [Fase](../F3_QR-GEN_EPICS.md)
- [PRD](../../PRD-QR-GEN.md)
- [F2](../../F2-Migracao-Dados-Validacao/F2_QR-GEN_EPICS.md) — concluida
