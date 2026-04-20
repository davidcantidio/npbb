# Relatorio final da meta-auditoria de importacao de leads

Data: 2026-04-20.

Este relatorio separa implementacao, aplicacao no ambiente, testes, metricas e execucao real. Onde nao ha prova, o item permanece aberto.

## 1. Estado final resumido

| Area | Estado verificavel |
| --- | --- |
| Evidencias versionadas | implementado em codigo |
| RLS central | implementado em codigo; nao aplicado no banco observado |
| Roles dedicadas | aplicado no banco/ambiente; observado em execucao real |
| Gates de runtime/deploy | implementado em codigo; validado por teste contratual |
| Storage fora do banco para novos uploads | implementado em codigo; validado por teste |
| Backfill historico de blobs | nao comprovado; 222 pendencias observadas |
| Worker dedicado | implementado em codigo/config; nao observado processando jobs reais |
| Performance | baseline atual coletado; sem ganho antes/depois comprovado |
| Auditoria de FKs/indices | observado em execucao real; sem indice novo justificado por metrica |
| Upload memory pressure | implementado em codigo; validado por teste direcionado |
| Preflight/hint legado | fluxo principal validado sem chamada browser; endpoint legado mantido temporariamente |
| Suite frontend completa | nao validada; 16 falhas permanecem |

## 2. O que foi realmente corrigido agora

Classificacao: implementado em codigo.

- Criada migration `8b6f4c2d9a1e_apply_central_leads_rls_policies.py` habilitando RLS e policies para `usuario`, `evento`, `ativacao`, `ativacao_lead`, `lead` e `lead_evento`.
- Ajustados pontos de runtime para setar contexto RLS antes de leituras sensiveis de usuario/autenticacao e rotas publicas/internas.
- Criados gates `verify_leads_runtime_env.py` e `verify_leads_hardening_db.py`.
- Adicionado alvo `make leads-deploy-gate`.
- Render blueprints passaram a executar gates antes de subir API e worker.
- SQL de roles passou a impor `NOBYPASSRLS` para `npbb_api` e `npbb_worker`.
- Upload de intake passou a usar spool/chunks em `upload_spool.py`, sem `upload.file.read()` integral no fluxo novo.
- Persistencia de payload passou a usar ponteiro de storage e limpar `arquivo_bronze` para novos lotes.
- Fallback local de storage em producao passou a falhar fechado.
- Worker recebeu logs estruturados, health file e configuracao explicita de retry/failure sleep.
- Scripts versionaveis foram criados para `pg_stat_statements`, EXPLAIN e auditoria de FKs.
- Testes automatizados direcionados foram adicionados/ajustados para backend e frontend.
- Evidencias foram versionadas em `auditoria/evidencias/`.

## 3. O que esta aplicado no banco/ambiente observado

Classificacao: aplicado no banco/ambiente; observado em execucao real.

- `pg_stat_statements` esta disponivel.
- Roles `npbb_api` e `npbb_worker` existem no Supabase observado.
- `npbb_api` e `npbb_worker` nao possuem `rolsuper`, `rolbypassrls`, `rolcreaterole` ou `rolcreatedb`.

Classificacao: observado em execucao real, com falha de aceite.

- `alembic_version` observado e `7a3c8d1e2f4b`, portanto a migration `8b6f4c2d9a1e` nao esta aplicada.
- `evento`, `ativacao`, `lead` e `lead_evento` estavam com `relrowsecurity=false`.
- Policies centrais novas nao estavam presentes em `pg_policies`.
- `lead_batches` ainda tem 222 blobs inline pendentes.

## 4. Validacao por testes

Classificacao: validado por teste.

- Backend direcionado: `35 passed in 46.43s`.
- Frontend direcionado do fluxo de importacao: `4 passed`, com `35 skipped` pelo filtro.

Classificacao: validado por teste, com falha.

- Suite completa `ImportacaoPage.test.tsx`: `16 failed, 23 passed`.
- Esta falha impede declarar que a pagina inteira esta coberta por regressao automatizada verde.

## 5. Performance

Classificacao: validado por EXPLAIN/metrica; observado em execucao real.

- Top 10 de `pg_stat_statements` foi coletado e versionado.
- EXPLAIN atual foi coletado para queries criticas.
- A maior pressao observada continua relacionada a consultas em `lead_batches` que incluem `arquivo_bronze`.
- `leads_silver` possui indice util para `batch_id, row_index`, mas a familia de query ainda apareceu com temp blocks em `pg_stat_statements`.

Classificacao: nao comprovado.

- Nao existe comparacao antes/depois completa nesta rodada.
- Nao foi declarada melhoria de performance.
- A correcao de performance fica dependente de aplicar migration/backfill, repetir captura e comparar planos equivalentes.

## 6. Auditoria de FKs e indices

Classificacao: observado em execucao real.

- As FKs criticas do fluxo lead/importacao observadas possuem indice util.
- FKs sem indice util em `ativacao_lead.gamificacao_id`, `evento.subtipo_id`, `evento.tipo_id` e `evento.divisao_demandante_id` foram classificadas como importantes, mas nao criticas para o fluxo atual de importacao.

Classificacao: decisao tecnica.

- Nenhum indice foi criado nesta rodada sem plano/metrica que justificasse o ganho.

## 7. Preflight/hint legado

Classificacao: validado por teste.

- O fluxo Bronze principal no frontend nao chama mais hash/preflight legado no browser nos testes direcionados.
- O hint aplicado vem do intake server-side.

Classificacao: decisao tecnica; risco residual documentado.

- Endpoint legado `GET /leads/batches/import-hint` foi mantido temporariamente para compatibilidade.
- Criterio de remocao: remover quando consumidores externos ou testes legados forem migrados para `POST /leads/batches/intake`.
- Prazo recomendado: proximo ciclo de hardening da importacao, antes de declarar fechamento definitivo da superficie legada.
- Ate a remocao, o endpoint deve permanecer autenticado, sem uso pelo fluxo principal e coberto por testes de acesso.

## 8. Riscos residuais

- RLS central nao esta aplicada no banco observado.
- Teste real de acesso cruzado entre agencias/perfis ainda nao foi executado contra o Supabase com a migration nova aplicada.
- Worker dedicado nao foi observado processando preview, commit e Gold fora da API.
- Backfill historico de `lead_batches.arquivo_bronze` nao foi concluido.
- Bucket, credenciais, politicas e retencao de storage nao foram observados operacionalmente; apenas gates e codigo foram endurecidos.
- Performance tem baseline atual, mas nao comparacao antes/depois.
- Suite frontend completa da pagina de importacao permanece com falhas.

## 9. Itens deliberadamente fora de escopo nesta execucao

- Aplicar DDL/migration diretamente no ambiente Supabase.
- Executar backfill historico em producao.
- Remover imediatamente o endpoint legado `import-hint`.
- Declarar ganho de performance sem nova captura comparativa.
- Declarar worker operacional sem logs reais de jobs processados.

## 10. Veredito

Classificacao final:

- Implementado em codigo: sim, para RLS central, gates, storage, upload spool, worker observability, scripts e testes direcionados.
- Aplicado no banco/ambiente: parcialmente. Roles dedicadas estao aplicadas; RLS central e backfill nao estao.
- Validado por teste: parcialmente. Backend direcionado e frontend direcionado passaram; suite frontend completa falhou.
- Validado por EXPLAIN/metrica: baseline atual coletado; sem ganho comprovado.
- Observado em execucao real: Supabase foi observado via consultas read-only; deploy real do worker/API com novas configs nao foi observado.

Conclusao: a correcao estrutural foi avancada no repositorio, mas o fechamento operacional ainda depende de aplicar a migration `8b6f4c2d9a1e`, executar backfill, capturar logs reais do worker e repetir metricas antes/depois.
