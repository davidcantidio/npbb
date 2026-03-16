# Evidencia F2-02-002 - Validacao pos-carga e viabilidade de rollback

**Issue:** ISSUE-F2-02-002 - Validar integridade pos-carga e procedimento de rollback  
**Data:** 2026-03-16  
**Status:** Concluido com sucesso

## Resumo

A validacao pos-carga foi executada com sucesso sobre o Supabase configurado no
`backend/.env`. O checklist confirmou:

- backup do Supabase preservado e legivel via `pg_restore --list`
- export local preservado e legivel via `pg_restore --list`
- `pg_restore --help` operacional para eventual restore
- `DIRECT_URL` e `DATABASE_URL` apontando para o mesmo projeto Supabase
- 71 tabelas `public` disponiveis no alvo e 71 tabelas com `TABLE DATA` no dump presentes no banco recarregado
- snapshot de contagem por tabela coletado sem voltar ao PostgreSQL local como fonte ativa

## Observacao operacional

O `backend/.env` ja continha `DATABASE_URL` e `DIRECT_URL`, mas nao continha
`LOCAL_DIRECT_URL`. Para gerar os artefatos desta rodada sem alterar o `.env`,
o dump local foi executado com override inline:

```bash
LOCAL_DIRECT_URL="postgresql+psycopg2://$USER@127.0.0.1:5432/npbb"
```

## Comandos executados

```bash
cd backend && LOCAL_DIRECT_URL="postgresql+psycopg2://$USER@127.0.0.1:5432/npbb" .venv/bin/python -m scripts.backup_export_migracao
cd backend && .venv/bin/python -m scripts.validacao_pos_carga_migracao
cd backend && PYTHONPATH=/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb:/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/backend SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_migracao_scripts.py
```

## Artefatos usados

| Artefato | Caminho |
|---|---|
| Backup do Supabase | `/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/artifacts_migracao/backup_supabase_20260316_181619.dump` |
| Export local | `/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/artifacts_migracao/export_local_20260316_181648.dump` |

## Checklist executado

| Verificacao | Resultado |
|---|---|
| Backup preservado e legivel | ok |
| Export local preservado e legivel | ok |
| `pg_restore --help` disponivel | ok |
| `DIRECT_URL` e `DATABASE_URL` conectam | ok |
| `DIRECT_URL` e `DATABASE_URL` apontam para o mesmo Supabase | ok |
| Tabelas `public` disponiveis no alvo | 71 |
| Tabelas com `TABLE DATA` no export presentes no alvo | 71 |
| Suite `tests/test_migracao_scripts.py` | 13 passed |

## Snapshot de contagem por tabela

| Tabela | Registros |
|---|---|
| `public.agencia` | 4 |
| `public.ativacao` | 6 |
| `public.ativacao_lead` | 0 |
| `public.attendance_access_control` | 0 |
| `public.conversao_ativacao` | 0 |
| `public.convidado` | 0 |
| `public.convite` | 0 |
| `public.cota_cortesia` | 6 |
| `public.cupom` | 0 |
| `public.data_quality_result` | 0 |
| `public.diretoria` | 41 |
| `public.divisao_demandante` | 4 |
| `public.dq_check_result` | 0 |
| `public.dq_inconsistency` | 0 |
| `public.event_publicity` | 2 |
| `public.event_sessions` | 0 |
| `public.evento` | 88 |
| `public.evento_landing_customization_audit` | 0 |
| `public.evento_tag` | 21 |
| `public.evento_territorio` | 3 |
| `public.events` | 0 |
| `public.festival_leads` | 0 |
| `public.formulario_landing_template` | 3 |
| `public.formulario_lead_campo` | 18 |
| `public.formulario_lead_config` | 3 |
| `public.funcionario` | 2 |
| `public.gamificacao` | 1 |
| `public.import_alias` | 0 |
| `public.ingestion` | 0 |
| `public.ingestion_evidence` | 0 |
| `public.ingestions` | 0 |
| `public.investimento` | 0 |
| `public.landing_analytics_event` | 0 |
| `public.lead` | 1710 |
| `public.lead_alias` | 2 |
| `public.lead_batches` | 0 |
| `public.lead_column_aliases` | 0 |
| `public.lead_conversao` | 0 |
| `public.lead_import_etl_preview_session` | 0 |
| `public.lead_reconhecimento_token` | 0 |
| `public.leads_silver` | 0 |
| `public.lineage_refs` | 0 |
| `public.metric_lineage` | 0 |
| `public.optin_transactions` | 0 |
| `public.password_reset_token` | 2 |
| `public.publicity_import_staging` | 2 |
| `public.questionario_opcao` | 0 |
| `public.questionario_pagina` | 1 |
| `public.questionario_pergunta` | 0 |
| `public.questionario_resposta` | 0 |
| `public.questionario_resposta_opcao` | 0 |
| `public.questionario_resposta_pergunta` | 0 |
| `public.solicitacao_ingresso` | 2 |
| `public.source` | 0 |
| `public.sources` | 0 |
| `public.status_evento` | 5 |
| `public.stg_access_control_sessions` | 0 |
| `public.stg_dimac_metrics` | 0 |
| `public.stg_lead_actions` | 0 |
| `public.stg_leads` | 0 |
| `public.stg_mtc_metrics` | 0 |
| `public.stg_optin_transactions` | 0 |
| `public.stg_social_metrics` | 0 |
| `public.subtipo_evento` | 20 |
| `public.tag` | 26 |
| `public.termo_uso_ativacao` | 0 |
| `public.territorio` | 4 |
| `public.ticket_category_segment_map` | 0 |
| `public.ticket_sales` | 0 |
| `public.tipo_evento` | 4 |
| `public.usuario` | 5 |

## Viabilidade de rollback

O rollback segue viavel sem executar restore destrutivo nesta rodada:

- o backup do Supabase permanece preservado em `artifacts_migracao/`
- `pg_restore --list` confirmou legibilidade do backup
- `pg_restore --help` confirmou tooling disponivel para eventual restore
- o runbook atualizado documenta o fluxo de restore via Supabase Dashboard ou `pg_restore`

## Gatilhos objetivos para rollback

- `DATABASE_URL` e `DIRECT_URL` deixarem de apontar para o mesmo projeto Supabase
- `backup_supabase` mais recente ficar ilegivel ou indisponivel para `pg_restore`
- qualquer tabela exportada no dump local ficar ausente ou inacessivel no Supabase recarregado
- checagens de conectividade ou contagem falharem durante a validacao final da F3

## Conclusao

A `ISSUE-F2-02-002` ficou apta para encerramento. A fase F2 pode sair de
`not_ready` para `pending` e seguir para auditoria formal, desde que a trilha
de auditoria use um commit SHA real e uma arvore limpa.
