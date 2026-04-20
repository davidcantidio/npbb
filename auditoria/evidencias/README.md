# Evidencias versionadas da auditoria de importacao de leads

Data de captura: 2026-04-20.

Esta pasta substitui evidencia local ignorada por Git por artefatos versionados. Cada arquivo separa explicitamente o tipo de alegacao:

- `implementado em codigo`: existe mudanca no repositorio.
- `aplicado no banco/ambiente`: foi observado no banco/ambiente alvo.
- `validado por teste`: houve execucao de teste automatizado com resultado registrado.
- `validado por EXPLAIN/metrica`: houve metrica ou plano observado.
- `observado em execucao real`: foi observado por consulta ou execucao contra ambiente real.

Arquivos:

- `supabase_rls_roles_storage_2026-04-20.md`: estado observado no Supabase para migrations, RLS, policies, roles e pendencias de storage.
- `pg_stat_statements_top10_current_2026-04-20.md`: top 10 queries atuais de `pg_stat_statements`.
- `explain_current_2026-04-20.md`: planos atuais capturados para queries criticas.
- `fk_index_audit_2026-04-20.md`: auditoria de FKs e indices uteis no fluxo de leads/importacao.
- `test_results_2026-04-20.md`: resultados dos testes automatizados executados.
- `deploy_runtime_worker_storage_2026-04-20.md`: evidencia de gates/configuracao de runtime, worker e storage e lacunas nao observadas.

Limitacao deliberada: nao ha baseline antes/depois completo de performance nesta rodada. Onde so existe estado atual, o arquivo declara isso como baseline corrente e nao como ganho comprovado.
