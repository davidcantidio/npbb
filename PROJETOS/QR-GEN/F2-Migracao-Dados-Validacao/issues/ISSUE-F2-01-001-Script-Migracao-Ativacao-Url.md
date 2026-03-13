---
doc_id: "ISSUE-F2-01-001-Script-Migracao-Ativacao-Url.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-13"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-01-001 - Script Migracao Ativacao URL

## User Story

Como DevOps ou desenvolvedor, quero um script de migracao que corrija registros `ativacao` com URL local persistida, para que zero QR codes com URL incorreta permanecam no banco apos o go-live.

## Contexto Tecnico

A tabela `ativacao` possui `landing_url`, `qr_code_url` e `url_promotor`. Registros criados em dev podem conter `localhost` ou `127.0.0.1`. O script deve usar `build_ativacao_public_urls()` e `build_qr_code_data_url()` com `PUBLIC_APP_BASE_URL` configurado para producao. Ver `backend/app/utils/urls.py` e `backend/app/services/landing_pages.py`.

## Plano TDD

- Red: Teste que valida script em dry-run nao persiste alteracoes
- Green: Script identifica, recalcula e atualiza registros quando executado sem dry-run
- Refactor: Extrair funcoes reutilizaveis se necessario

## Criterios de Aceitacao

- Given registros `ativacao` com `landing_url` ou `url_promotor` contendo localhost/127.0.0.1, When executo o script com `PUBLIC_APP_BASE_URL` configurado, Then os registros sao atualizados com URL correta
- Given dry-run ativado, When executo o script, Then nenhuma alteracao e persistida
- Given o script executado com sucesso, When consulto o banco, Then zero registros com localhost em `landing_url` ou `url_promotor`

## Definition of Done da Issue
- [x] Script de migracao executavel
- [x] Dry-run funcional
- [x] Rollback documentado
- [x] Teste de validacao passando

## Tasks Decupadas

- [x] T1: Criar arquivo de data migration Alembic ou script standalone com esqueleto
- [x] T2: Implementar query para identificar ativacao com landing_url ou url_promotor contendo localhost/127.0.0.1
- [x] T3: Implementar recalculo de landing_url, url_promotor e qr_code_url usando build_ativacao_public_urls e build_qr_code_data_url
- [x] T4: Implementar persistencia das alteracoes em transacao
- [x] T5: Adicionar parametro dry-run (env var ou CLI) e documentar uso

## Instructions por Task

### T1

- objetivo: criar arquivo de data migration Alembic ou script standalone com esqueleto executavel
- precondicoes: revision base do Alembic identificada; ambiente com acesso ao banco
- arquivos_a_ler_ou_tocar:
  - `backend/alembic/versions/` (se Alembic) ou `backend/scripts/` (se standalone)
  - `backend/alembic/env.py`
- passos_atomicos:
  1. Decidir entre Alembic data migration ou script standalone (recomendacao: script standalone para dry-run mais simples)
  2. Se Alembic: criar `alembic revision -m "fix_ativacao_url_localhost"` e editar upgrade/downgrade
  3. Se standalone: criar `backend/scripts/fix_ativacao_url_localhost.py` com `if __name__ == "__main__"` e parse de args
  4. Garantir que o script carregue `backend/.env` e use `DATABASE_URL` ou `DIRECT_URL`
- comandos_permitidos:
  - `cd backend && alembic revision -m "fix_ativacao_url_localhost"`
  - `cd backend && python -m scripts.fix_ativacao_url_localhost --dry-run`
- resultado_esperado: arquivo criado, executavel sem erro (pode nao fazer alteracoes ainda)
- testes_ou_validacoes_obrigatorias:
  - script executa sem excecao
- stop_conditions:
  - parar se houver conflito de revision no Alembic
  - parar se DATABASE_URL nao estiver configurado

### T2

- objetivo: implementar query para identificar ativacao com landing_url ou url_promotor contendo localhost ou 127.0.0.1
- precondicoes: T1 concluida; conexao com banco disponivel
- arquivos_a_ler_ou_tocar:
  - `backend/app/models/models.py` — modelo Ativacao
  - script ou migration criado em T1
- passos_atomicos:
  1. Usar SQL ou SQLModel/Session para selecionar ativacao onde `landing_url LIKE '%localhost%' OR landing_url LIKE '%127.0.0.1%' OR url_promotor LIKE '%localhost%' OR url_promotor LIKE '%127.0.0.1%'`
  2. Retornar lista de ids ou objetos
  3. Logar ou imprimir quantidade de registros afetados
- comandos_permitidos:
  - `cd backend && python -m scripts.fix_ativacao_url_localhost --dry-run`
- resultado_esperado: script identifica e reporta quantidade de registros a corrigir
- testes_ou_validacoes_obrigatorias:
  - em banco com registros de teste, a contagem e correta
- stop_conditions:
  - parar se a query falhar por schema divergente

### T3

- objetivo: implementar recalculo de landing_url, url_promotor e qr_code_url usando build_ativacao_public_urls e build_qr_code_data_url com PUBLIC_APP_BASE_URL
- precondicoes: T2 concluida; PUBLIC_APP_BASE_URL deve estar em env para producao
- arquivos_a_ler_ou_tocar:
  - `backend/app/utils/urls.py` — build_ativacao_public_urls
  - `backend/app/services/qr_code.py` — build_qr_code_data_url
  - script ou migration criado em T1
- passos_atomicos:
  1. Garantir que PUBLIC_APP_BASE_URL esteja setado (ou usar valor padrao de producao para a migracao)
  2. Para cada ativacao_id da lista, chamar `build_ativacao_public_urls(ativacao_id)` para obter landing_url e url_promotor
  3. Chamar `build_qr_code_data_url(landing_url)` para obter qr_code_url
  4. Montar dicionario de valores a atualizar
- comandos_permitidos:
  - `cd backend && python -c "from app.utils.urls import build_ativacao_public_urls; print(build_ativacao_public_urls(1))"`
- resultado_esperado: para cada id, valores corretos calculados
- testes_ou_validacoes_obrigatorias:
  - valores calculados nao contem localhost quando PUBLIC_APP_BASE_URL esta setado
- stop_conditions:
  - parar se PUBLIC_APP_BASE_URL nao estiver setado e ambiente for producao (opcional: usar valor default app.npbb.com.br)

### T4

- objetivo: implementar persistencia das alteracoes em transacao
- precondicoes: T3 concluida
- arquivos_a_ler_ou_tocar:
  - script ou migration
  - `backend/app/models/models.py` — Ativacao
- passos_atomicos:
  1. Abrir sessao/transacao
  2. Para cada ativacao, executar UPDATE em landing_url, url_promotor e qr_code_url
  3. Commit da transacao
  4. Em caso de erro, rollback
- comandos_permitidos:
  - `cd backend && python -m scripts.fix_ativacao_url_localhost` (sem dry-run, em ambiente de teste)
- resultado_esperado: registros atualizados no banco
- testes_ou_validacoes_obrigatorias:
  - apos execucao, query de T2 retorna 0 registros
- stop_conditions:
  - parar e fazer rollback se qualquer UPDATE falhar

### T5

- objetivo: adicionar parametro dry-run (env var ou CLI) e documentar uso
- precondicoes: T4 concluida
- arquivos_a_ler_ou_tocar:
  - script ou migration
  - `docs/` ou README do script
- passos_atomicos:
  1. Adicionar `--dry-run` ou `DRY_RUN=1` para pular commit
  2. Quando dry-run, executar toda a logica exceto commit; logar o que seria alterado
  3. Documentar no topo do script ou em docs: como executar, pre-requisitos (PUBLIC_APP_BASE_URL), rollback
- comandos_permitidos:
  - `cd backend && python -m scripts.fix_ativacao_url_localhost --dry-run`
  - `cd backend && python -m scripts.fix_ativacao_url_localhost`
- resultado_esperado: dry-run nao persiste; execucao normal persiste
- testes_ou_validacoes_obrigatorias:
  - dry-run nao altera banco
  - documentacao clara
- stop_conditions:
  - parar se dry-run estiver ativo e houver tentativa de commit

## Arquivos Reais Envolvidos

- `backend/app/utils/urls.py`
- `backend/app/services/qr_code.py`
- `backend/app/services/landing_pages.py`
- `backend/app/models/models.py`
- `backend/scripts/fix_ativacao_url_localhost.py` ou `backend/alembic/versions/xxx_fix_ativacao_url_localhost.py`

## Artifact Minimo

- Script executavel com dry-run
- Documentacao de uso e rollback

## Dependencias

- [Intake](../../INTAKE.md)
- [Epic](../EPIC-F2-01-Migracao.md)
- [Fase](../F2_QR-GEN_EPICS.md)
- [PRD](../../PRD-QR-GEN.md)
- [F1](../../F1-Levantamento-Configuracao/F1_QR-GEN_EPICS.md) — concluida
