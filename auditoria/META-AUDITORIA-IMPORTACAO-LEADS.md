# Meta-Auditoria do Mecanismo de Importacao de Leads

Commit auditado: `a4160b6..76d5ee7` (`Harden leads import: storage, RLS, worker, and dashboard performance`).

Prompt de julgamento: `metaaudit.md`.

Escopo: importacao de leads, hardening Supabase/Postgres, RLS, storage, worker, frontend, dashboard/query tuning, staging/merge/COPY e evidencia de validacao.

Comandos de verificacao usados: `git diff --stat a4160b6 76d5ee7`, `git diff --name-status a4160b6 76d5ee7`, `rg`/`Select-String` nos arquivos alterados, leitura de `artifacts_migracao/explain_leads_critical_output.txt`, `git ls-files artifacts_migracao`, `git check-ignore -v artifacts_migracao/explain_leads_critical_output.txt`.

Limite de evidencia: esta meta-auditoria nao aplicou migrations, nao conectou ao Supabase remoto e nao reexecutou testes automatizados. O julgamento de execucao se baseia em diff, scripts, artefatos locais e ausencia/presenca de provas versionadas.

## 1. VEREDITO EXECUTIVO

Julgamento final: **PARCIALMENTE BEM-SUCEDIDA, COM EVIDENCIA FRACA E RISCO REAL DE COMPLIANCE DE PAPEL**.

Justificativa curta e brutal: houve codigo real, SQL real e mudancas arquiteturais concretas. Nao foi apenas narrativa. Mas a auditoria original vendeu prova de performance e hardening operacional com mais certeza do que a trilha material sustenta. O commit tem 26 arquivos alterados, 2084 insercoes e 192 remocoes, incluindo migration, worker, storage e dashboard. Isso e execucao real. O problema e que a validacao e fraca: nenhum teste foi adicionado/alterado no commit, o artefato de `EXPLAIN ANALYZE` esta ignorado pelo Git, nao ha baseline antes/depois versionado, nao ha prova de migration aplicada, nao ha prova de roles aplicadas, nao ha prova de worker rodando, e a RLS em tabelas centrais (`evento`, `ativacao`, `lead`, `lead_evento`) foi desabilitada em vez de resolvida.

Sentenca: a entrega corrigiu partes importantes, mas supervendeu impacto medido. Nao e cosmetica. Tambem nao e plenamente bem-sucedida. E uma intervencao parcial com boa direcao tecnica, execucao material e validacao insuficiente.

## 2. MATRIZ DE AVALIACAO

| Eixo | Nota | Classificacao | Evidencia | Falhas | Conclusao |
| --- | ---: | --- | --- | --- | --- |
| Qualidade do diagnostico | 7/10 | ACEITAVEL | O diff ataca problemas reais: conexao/pooler em `backend/app/db/database.py:51`, storage fora de blob em `backend/app/services/imports/payload_storage.py:176`, worker em `backend/scripts/run_leads_worker.py:1`, dashboard em `backend/app/routers/dashboard_leads.py:72`, frontend em `frontend/src/pages/leads/ImportacaoPage.tsx:826`. | O diagnostico tratou varias hipoteses como provadas. O alvo `.insert().select()` nao existia no stack auditado; o problema real era leitura gorda/roundtrip de outra natureza. | Encontrou defeitos importantes, mas misturou evidencia real com inferencia. |
| Qualidade da priorizacao | 7/10 | RAZOAVEL | P0s escolhidos fazem sentido: runtime/RLS, blob inline, worker, query tuning e frontend. | RLS e performance foram priorizadas corretamente, mas a solucao de RLS deixou tabelas criticas desligadas e a performance ficou sem baseline versionado. | Priorizacao lucida no tema, incompleta na demonstracao. |
| Qualidade da execucao | 6.5/10 | EXECUCAO PARCIAL | Commit adiciona migration `3f7b9c2d1e4a`, migration corretiva `7a3c8d1e2f4b`, storage adapter, scripts de backfill/verificacao, worker e mudancas no frontend/backend. | Nada prova aplicacao em ambiente real. `render.yaml` cria worker, mas nao prova deploy. `OBJECT_STORAGE_BACKEND` fica `sync: false`; se nao configurado, o codigo defaulta para storage local. | Houve execucao real, mas nao fechamento operacional. |
| Qualidade da evidencia | 4/10 | FRACA | Existe `artifacts_migracao/explain_leads_critical_output.txt` com `EXPLAIN ANALYZE`, e script `backend/scripts/run_critical_explains.py:67` gera EXPLAIN. | O artefato esta ignorado por `.gitignore:30`, nao versionado. Nao ha antes/depois. Nao ha saida de `verify_leads_hardening_db.py`. Nao ha log de worker. Nao ha output de testes. | Evidencia suficiente para dizer "foi mexido"; insuficiente para dizer "melhorou como alegado". |
| Qualidade da validacao | 3/10 | INSUFICIENTE | Foram criados scripts de verificacao: `backend/scripts/verify_leads_hardening_db.py` e `backend/scripts/run_critical_explains.py`. | O commit nao altera nenhum arquivo de teste. A alegacao de "143 testes passaram" nao esta versionada. Scripts de validacao nao equivalem a validacao executada. | O ponto mais fraco da auditoria original. |
| Impacto real no sistema | 6/10 | IMPACTO MODERADO, NAO COMPROVADO | Storage remove novo blob inline (`payload_storage.py:200`, `payload_storage.py:233`), frontend deixa de calcular hash antes do upload (`ImportacaoPage.tsx:826`), API passa a enfileirar Gold (`leads.py:2499`), worker faz loop dedicado (`run_leads_worker.py:48`). | Sem metricas antes/depois. O EXPLAIN local mostra `data_compra` ainda com sort e `Execution Time: 90.917 ms`. O backend ainda faz `upload.file.read()` inteiro em `lead_batch_intake_service.py:329`. | Impacto provavel em alguns caminhos, mas nao medido de forma competente. |
| Debitos e falsos positivos | 5/10 | PARCIAL | Ha acertos reais: storage, worker, guards, policies em tabelas de importacao. | Falso positivo forte: vender RLS "real" enquanto desabilita RLS em `evento`, `ativacao`, `lead`, `lead_evento` (`3f7b9c2d1e4a:20`, `3f7b9c2d1e4a:195`). Falso positivo: vender EXPLAIN antes/depois sem baseline versionado. | Houve melhoria, mas tambem maquiagem por linguagem confiante. |
| Risco de compliance de papel | 7/10 | ALTO | Criaram scripts, migration e config. | Scripts nao provam execucao. Roles SQL nao provam aplicacao. Worker no YAML nao prova processo vivo. Backfill nao prova migracao de blobs historicos. | O risco de "parece governado, mas nao esta provado" e alto. |

## 3. AUDITORIA DA AUDITORIA

### Promessa: API no pooler :6543, role dedicada e worker em DIRECT_URL

- Evidencia apresentada: guard em `backend/app/db/database.py:51` rejeita Supabase fora da porta 6543 para `DATABASE_URL`; `database.py:74` rejeita role `postgres`; `database.py:153` separa `WORKER_DATABASE_URL`/`DIRECT_URL`; `.env.example:2-11` documenta o contrato; `backend/scripts/sql/create_npbb_runtime_roles.sql:13-17` cria roles `npbb_api` e `npbb_worker`.
- Evidencia ausente: prova de SQL executado, prova de role sem `BYPASSRLS` no banco real, prova de variaveis efetivas no deploy.
- Julgamento: **APROVADA COM RESSALVAS**. O codigo bloqueia configuracao ruim, mas a entrega nao prova que o ambiente foi corrigido.

### Promessa: RLS real e otimizada

- Evidencia apresentada: `set_db_request_context()` usa `set_config('app.user_id')`, `app.user_type` e `app.agencia_id` em `backend/app/db/database.py:233-245`; `get_current_user()` injeta contexto depois de autenticar em `backend/app/core/auth.py:99-107`; migration cria helper functions em `3f7b9c2d1e4a:77-106`; policies usam `(select public.npbb_current_user_id())`, por exemplo `3f7b9c2d1e4a:241` e `3f7b9c2d1e4a:317`.
- Evidencia ausente: inventario de policies reais pos-deploy, output de `pg_policies`, plano de execucao com RLS ativa, teste de acesso agencia A contra agencia B, prova de role sem bypass.
- Falha material: a migration desabilita RLS em `evento`, `ativacao`, `lead`, `lead_evento` (`3f7b9c2d1e4a:20`, `3f7b9c2d1e4a:195-197`), embora a auditoria tenha vendido hardening de fluxo de leads/eventos.
- Julgamento: **INSUFICIENTE**. Melhor que RLS vazia, mas nao e revisao completa de RLS. E uma contencao parcial em tabelas auxiliares de importacao, com desligamento em tabelas centrais.

### Promessa: blobs Bronze/ETL fora do banco

- Evidencia apresentada: modelos ganham ponteiros `bronze_storage_*` em `backend/app/models/lead_batch.py:56-60` e `file_storage_*` em `backend/app/models/lead_public_models.py:360-364`; `persist_batch_payload()` zera `arquivo_bronze` em `backend/app/services/imports/payload_storage.py:176-200`; `persist_etl_job_payload()` zera `file_blob` em `payload_storage.py:210-233`; backfill existe em `backend/scripts/backfill_import_payloads_to_storage.py`.
- Evidencia ausente: output do backfill, contagem de blobs migrados, prova de bucket criado, prova de configuracao de storage em producao.
- Falha material: `.env.example:68` defaulta `OBJECT_STORAGE_BACKEND=local`; `render.yaml` deixa `OBJECT_STORAGE_BACKEND` como `sync: false`. Sem variavel real, o deploy pode cair em storage local/efemero.
- Julgamento: **APROVADA COM RESSALVAS**. O codigo de transicao e real. O fechamento operacional nao esta provado.

### Promessa: worker dedicado no lugar de BackgroundTasks/thread

- Evidencia apresentada: `BackgroundTasks` foi removido do diff em `backend/app/routers/leads.py`; preview/commit agora chamam inline apenas se `TESTING` ou flag explicita (`leads.py:167`, `leads.py:1741`, `leads.py:1853`); Gold usa `queue_pipeline_batch(batch)` em `leads.py:2499`; worker dedicado existe em `backend/scripts/run_leads_worker.py:1` e loopa em `run_leads_worker.py:48`; claims usam `skip_locked` em `job_repository.py:73` e `lead_pipeline_service.py:1084`.
- Evidencia ausente: log de processo, healthcheck, retry observado, job real completado pelo worker, prova de deploy do worker.
- Falha residual: `executar_pipeline_gold_em_thread()` ainda existe em `lead_pipeline_service.py:2198`, embora aparentemente sem uso pela API.
- Julgamento: **APROVADA COM RESSALVAS**. A direcao estrutural e correta; a operabilidade nao foi provada.

### Promessa: frontend desonerado

- Evidencia apresentada: diff remove `computeFileSha256Hex` e `getLeadImportMetadataHint` do fluxo da pagina; `ImportacaoPage.tsx:826` chama `createLeadBatchIntake`; `ImportacaoPage.tsx:845-846` aplica `hint_applied` retornado pelo backend; backend calcula SHA-256 em `lead_batch_intake_service.py:329-331`.
- Evidencia ausente: teste de frontend provando que selecao de arquivo nao dispara hash/preflight; medicao de tempo/browser.
- Falha material: as funcoes `getLeadImportMetadataHint()` e `computeFileSha256Hex()` continuam exportadas em `frontend/src/services/leads_import.ts:549` e `:568`, e o endpoint `/batches/import-hint` continua ativo em `backend/app/routers/leads.py:2032`. Isso preserva compatibilidade, mas tambem preserva superficie antiga.
- Julgamento: **APROVADA COM RESSALVAS**. O fluxo principal foi desonerado; a remocao nao e completa.

### Promessa: query tuning e indices

- Evidencia apresentada: filtros por range substituem parte do uso de `date()` em `dashboard_leads.py:72-76` e `dashboard_leads_report.py:82-91`; migration cria `idx_lead_data_compra_not_null` em `3f7b9c2d1e4a:163-170`; migration remove indice redundante `ix_leads_silver_leads_silver_batch_id` em `3f7b9c2d1e4a:171-174`; `run_critical_explains.py:67` executa `EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)`.
- Evidencia ausente: top 10 queries com `pg_stat_statements`, baseline antes, comparacao depois, output versionado, decisao formal para FKs criticas.
- Falha material: `dashboard_leads.py:159` ainda usa `func.date(Lead.data_criacao)` para agrupamento diario; pode ser aceitavel para agregacao, mas nao foi acompanhado de plano. O artefato local pos-deploy mostra `idx_lead_data_compra_not_null` sendo usado, mas ainda com sort e `Execution Time: 90.917 ms` em `artifacts_migracao/explain_leads_critical_output.txt`.
- Julgamento: **INSUFICIENTE COMO PROVA DE OTIMIZACAO**. Ha tuning real, mas a prova e fraca.

### Promessa: staging + merge + COPY

- Evidencia apresentada: `lead_import_etl_staging` existe no modelo com indices por `session_token`, `validation_status`, `merge_status` e `dedupe_key` em `backend/app/models/lead_public_models.py:380-385`; `staging_repository.py:23-24` define thresholds de COPY; `staging_repository.py:144` usa `COPY lead_import_etl_staging`; `commit_service.py:119` reporta `merge_strategy="backend_staging_merge"`.
- Evidencia ausente: demonstracao de que isso foi criado pela auditoria auditada. O commit `76d5ee7` nao altera `staging_repository.py` nem `commit_service.py`; portanto a entrega pode ter apenas reaproveitado capacidade anterior.
- Julgamento: **CONFIRMADO COMO EXISTENTE, NAO CONFIRMADO COMO CORRECAO DESTA AUDITORIA**. Vender isso como intervencao nova seria exagero.

### Promessa: eliminacao de `.insert/.update/.upsert/.delete().select()`

- Evidencia apresentada: scan focado em `frontend`, `backend/app` e `backend/scripts` nao encontrou ocorrencias desse padrao Supabase client.
- Evidencia ausente: matriz de equivalentes SQLAlchemy por fluxo de escrita. Ha muitos `session.refresh()` e `select()` no repo, mas nao sao o mesmo anti-pattern.
- Julgamento: **ALVO MAL FORMULADO PARA ESTE STACK**. A auditoria acertou ao atacar leituras gordas e preflight, mas o criterio `.select()` nao era o gargalo central aqui.

## 4. FALSOS POSITIVOS E MAQUIAGEM

- **"RLS real" supervendida**: ha policies em tabelas de importacao, mas `evento`, `ativacao`, `lead` e `lead_evento` foram explicitamente colocadas em `RLS_DISABLED_TABLES`. Chamar isso de revisao completa de RLS e maquiagem.
- **"Prova de melhoria" supervendida**: o script de `EXPLAIN` existe, mas a saida versionada nao existe. O arquivo local esta em diretorio ignorado. Sem baseline antes/depois, a melhoria alegada e hipotese.
- **"COPY integrado" supervendido como entrega nova**: `COPY` existe em `staging_repository.py`, mas esse arquivo nao entrou no diff `a4160b6..76d5ee7`. E capacidade existente, nao prova de correcao recente.
- **"Worker dedicado" parcialmente maquiado**: o codigo do worker existe e o YAML declara worker, mas nao ha log, supervisao, metricas, nem prova de job executado fora da API.
- **"Blobs fora do banco" parcialmente maquiado**: novos uploads tendem a sair do blob inline, mas o default local e a ausencia de prova de bucket/backfill deixam risco operacional.
- **"Frontend desonerado" parcial**: a tela principal para de calcular hash antes do upload, mas o backend continua lendo arquivo inteiro em memoria (`upload.file.read()`), e o endpoint/servico antigo continuam vivos.
- **"143 testes passaram" sem lastro**: o commit nao altera nenhum arquivo de teste, e nao ha output de teste versionado ou anexado na trilha auditada.

## 5. CONFIRMACOES REAIS

- Houve diff real e amplo: 26 arquivos, 2084 insercoes, 192 remocoes.
- O guard de runtime Supabase e real: `DATABASE_URL` de API em Supabase precisa passar pela porta 6543 e nao usar role `postgres` (`database.py:51-74`).
- O contexto RLS por request existe: `set_db_request_context()` usa `set_config` e `auth.py` chama isso para usuario autenticado.
- Policies foram criadas para `lead_batches`, `leads_silver`, `lead_import_etl_preview_session`, `lead_import_etl_job`, `lead_import_etl_staging` e `lead_column_aliases`.
- Storage adapter existe e zera os campos blob nos novos caminhos (`payload_storage.py:200`, `payload_storage.py:233`).
- Backfill de blobs historicos existe como script idempotente.
- Worker dedicado existe e usa claims com `skip_locked`.
- O fluxo principal de `ImportacaoPage` nao calcula mais hash SHA-256 no browser antes do upload.
- O endpoint de Gold nao dispara mais thread/background task diretamente; ele enfileira o batch.
- Ha script de EXPLAIN pos-deploy e um artefato local gerado, ainda que ignorado pelo Git.

## 6. FALHAS ESTRUTURAIS REMANESCENTES

- **RLS incompleta em tabelas centrais**: `evento`, `ativacao`, `lead`, `lead_evento` foram desabilitadas. Isso pode ser decisao pragmatica, mas nao pode ser vendido como RLS completa.
- **Ausencia de baseline de performance**: sem top queries antes, sem top queries depois, sem `pg_stat_statements` versionado, sem comparacao objetiva.
- **EXPLAIN pos-deploy nao versionado**: `artifacts_migracao/explain_leads_critical_output.txt` existe localmente, mas `.gitignore:30` ignora `artifacts_migracao/`.
- **Data_compra ainda suspeito**: o EXPLAIN local mostra `idx_lead_data_compra_not_null` usado, mas com `Sort Method: top-N heapsort` e `Execution Time: 90.917 ms`. Isso nao sustenta uma vitoria limpa de tuning.
- **Storage operacional nao fechado**: bucket, credenciais e backend real nao estao provados. Default local em `.env.example` e `sync: false` no Render deixam margem para storage efemero.
- **Backfill nao comprovado**: script existe, mas nao ha output de execucao nem contagem de migrados.
- **Worker nao comprovado em operacao**: codigo e YAML existem; falta log, healthcheck, metricas, dead-letter ou evidencia de job real.
- **Sem teste novo no commit**: nenhum arquivo de teste foi alterado/adicionado no range auditado.
- **Leitura inteira de upload continua no backend**: `lead_batch_intake_service.py:329` ainda faz `upload.file.read()`. A carga saiu do browser, mas nao virou streaming robusto.
- **FK audit nao demonstrada**: ha indices existentes e um novo indice parcial, mas nao ha relatorio de FKs sem indice nem decisao por FK critica.
- **Endpoint de hint antigo permanece**: `/leads/batches/import-hint` ainda existe; se o objetivo era eliminar preflight, a compatibilidade precisa ter prazo ou criterio de remocao.

## 7. SENTENCA POR PRIORIDADE

| Prioridade original | Sentenca | Justificativa tecnica |
| --- | --- | --- |
| P0 - Runtime/pooler/roles | APROVADA COM RESSALVAS | Guard e script SQL existem. Falta prova de aplicacao das roles e variaveis reais. |
| P0 - RLS real | INSUFICIENTE | Policies existem em tabelas de importacao, mas tabelas centrais de leads/eventos tiveram RLS desabilitada. Sem `pg_policies` pos-deploy. |
| P0 - Blobs fora do banco | APROVADA COM RESSALVAS | Novo caminho zera blobs e grava ponteiro. Falta bucket/backfill/prova de producao. |
| P0 - Worker dedicado | APROVADA COM RESSALVAS | Codigo, claim e Render worker existem. Falta prova operacional e observabilidade de execucao. |
| P0 - Desonerar frontend | APROVADA COM RESSALVAS | Tela principal nao calcula hash/preflight; backend assumiu hash/hint. Mas servico/endpoint antigo persistem e backend le arquivo inteiro. |
| P0 - Query tuning | INSUFICIENTE | Houve reescrita parcial e indice. Sem baseline antes/depois versionado; EXPLAIN local e apenas pos e ignorado. |
| P1 - Indices e FKs | INSUFICIENTE | Indice parcial e remocao de indice redundante existem. Nao ha auditoria material de FKs criticas. |
| P1 - Staging/merge/COPY | APROVADA COM RESSALVAS | Fluxo existe e parece serio, mas boa parte ja existia antes do commit auditado. Nao pode ser creditado integralmente a esta auditoria. |
| P1 - Eliminar roundtrip inutil | APROVADA COM RESSALVAS | Nao havia `.insert().select()` Supabase client; o roundtrip real atacado foi outro. A auditoria deveria ter dito isso com mais precisao. |

## 8. PLANO DE CORRECAO DA PROPRIA AUDITORIA

1. Refazer a validacao de performance com pacote versionado:
   - salvar `pg_stat_statements` top 10 antes/depois;
   - salvar `EXPLAIN (ANALYZE, BUFFERS)` antes/depois para cada query alegadamente corrigida;
   - versionar o artefato em caminho nao ignorado, por exemplo `auditoria/evidencias/`.

2. Corrigir a narrativa de RLS:
   - declarar explicitamente que `evento`, `ativacao`, `lead`, `lead_evento` ficaram sem RLS;
   - criar plano e policies reais para essas tabelas ou justificar formalmente por que saem do escopo;
   - rodar e anexar `pg_policies`, `pg_class.relrowsecurity`, `rolbypassrls` e testes de acesso por perfil.

3. Provar deploy operacional:
   - anexar output de `verify_leads_hardening_db.py`;
   - anexar evidencia de `npbb_api` e `npbb_worker` sem `BYPASSRLS`;
   - anexar logs do worker processando preview, commit e Gold;
   - anexar status de bucket e backfill de blobs historicos.

4. Fechar storage como operacao, nao apenas codigo:
   - configurar `OBJECT_STORAGE_BACKEND=supabase` no ambiente real;
   - registrar bucket, chave, politicas de acesso e retencao;
   - rodar backfill e publicar contagem de pendencias zero antes de considerar a correcao completa.

5. Transformar os scripts em gate:
   - `run_critical_explains.py` deve falhar se plano esperado nao aparecer;
   - `verify_leads_hardening_db.py` deve virar check de CI/deploy;
   - teste automatizado deve cobrir: API rejeita `DATABASE_URL` ruim, frontend nao chama hash/hint preflight, worker reclama jobs, storage zera blobs novos, RLS bloqueia agencia indevida.

6. Reavaliar gargalo de upload:
   - trocar `upload.file.read()` inteiro por leitura spool/streaming quando o tamanho justificar;
   - medir memoria e latencia em arquivo grande;
   - manter browser apenas como upload/configuracao/status, mas tambem impedir que a API vire gargalo de memoria.

7. Auditar FKs de verdade:
   - produzir query de catalogo para FKs sem indice;
   - classificar cada FK do fluxo de leads/importacao;
   - criar/remover indices com justificativa por query e plano, nao por intuicao.

8. Corrigir o laudo original:
   - substituir afirmacoes absolutas por estados verificaveis: "implementado em codigo", "aplicado no banco", "validado por EXPLAIN", "observado em deploy";
   - separar capacidade preexistente de correcao introduzida no commit;
   - nao contar scripts como prova enquanto nao houver output verificavel.
