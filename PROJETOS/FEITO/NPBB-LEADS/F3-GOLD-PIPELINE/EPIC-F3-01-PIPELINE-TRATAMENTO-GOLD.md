EPIC-F3-01 — Pipeline de Tratamento Gold
projeto: NPBB-LEADS | fase: F3 | status: ✅
depende de: F2 concluída (leads_silver preenchido, stage=silver)

1. Resumo
Integrar o lead_pipeline existente (PROJETOS/lead_pipeline/) como motor de
tratamento Gold. Ao ser acionado, o pipeline lê os dados Silver do lote, executa
normalização, deduplicação e validação, promove os leads aprovados para a tabela
leads (Gold), persiste o relatório de qualidade no lote e atualiza o stage
para gold. O processo roda como background task FastAPI para não bloquear a UI.
2. Contexto Arquitetural

PROJETOS/lead_pipeline/pipeline.py — run_pipeline(PipelineConfig) → PipelineResult
PipelineConfig: recebe lote_id, input_files (lista de Path), output_root
PipelineResult: status, decision, exit_code, consolidated_path, report_path
O pipeline lê arquivos CSV/XLSX do disco — estratégia: materializar leads_silver
como CSV temporário em /tmp/npbb_pipeline/{batch_id}/ e passar para o pipeline
Tabela leads existente = destino Gold; verificar campos compatíveis com
REQUIRED_COLUMNS do pipeline (nome, cpf, data_nascimento, email, telefone,
evento, tipo_evento, local, data_evento)
Background tasks: usar fastapi.BackgroundTasks ou asyncio simples

3. Riscos

run_pipeline() é síncrono e CPU-bound — rodar em thread pool (run_in_executor)
para não bloquear o event loop do FastAPI
Arquivos temporários devem ser limpos após o pipeline (ou mantidos para auditoria)
FAIL no pipeline: nenhum lead é inserido na tabela leads; apenas pipeline_report
é salvo no lote e stage volta para silver (permitir reprocessamento futuro)
Campos da tabela leads existente podem não bater 1:1 com REQUIRED_COLUMNS —
mapear diferenças antes de inserir

4. Definition of Done

 POST /leads/batches/{id}/executar-pipeline dispara background task
 Pipeline materializa leads_silver como CSV temporário e executa run_pipeline()
 Leads aprovados (decision=promote) inseridos em tabela leads com batch_id
 Lotes com FAIL: nenhum lead inserido, stage permanece silver, report salvo
 lead_batches.pipeline_report preenchido com conteúdo do report.json
 lead_batches.pipeline_status e stage atualizados corretamente
 UI exibe status do pipeline e link para relatório por lote
 CI verde sem regressão


Issues
NPBB-F3-01-001 — Serviço de Execução do Pipeline (Backend)
tipo: feature | sp: 5 | prioridade: alta | status: ✅
depende de: NPBB-F2-01-002 (leads_silver existentes)
Descrição:
Criar backend/app/services/lead_pipeline_service.py com função
executar_pipeline_gold(batch_id, db) que: (1) materializa leads_silver como
CSV temporário, (2) chama run_pipeline() em thread pool, (3) lê o resultado,
(4) insere leads Gold na tabela leads se decision=promote, (5) atualiza o lote.
Critérios de Aceitação:

 Função materializa leads_silver.dados_brutos como CSV com colunas de REQUIRED_COLUMNS
 run_pipeline() executado via loop.run_in_executor(None, ...) (não bloqueia event loop)
 Leads com decision=promote inseridos em leads com batch_id preenchido
 lead_batches.pipeline_report = conteúdo do report.json (jsonb)
 lead_batches.pipeline_status = "pass" | "pass_with_warnings" | "fail"
 stage = "gold" se promote, permanece "silver" se fail
 Arquivos temporários em /tmp/npbb_pipeline/{batch_id}/ limpos após execução

Tarefas:

 T1: Criar backend/app/services/lead_pipeline_service.py
 T2: Função materializar_silver_como_csv(batch_id, db) → Path
(lê leads_silver, escreve CSV com colunas canônicas em /tmp)
 T3: Função executar_pipeline_gold(batch_id, db)
(chama run_pipeline via executor, processa PipelineResult)
 T4: Mapear colunas do CSV Gold para campos da tabela leads existente
(inspecionar modelo Lead em backend/app/models/)
 T5: Inserir leads aprovados em bulk na tabela leads
 T6: Atualizar LeadBatch (pipeline_report, pipeline_status, stage)
 T7: Limpar /tmp após execução

Notas técnicas:
pythonimport asyncio
from lead_pipeline.pipeline import run_pipeline, PipelineConfig

loop = asyncio.get_event_loop()
result = await loop.run_in_executor(None, run_pipeline, config)
Importar run_pipeline direto — PYTHONPATH já inclui raiz do repo.

NPBB-F3-01-002 — Endpoint POST /leads/batches/{id}/executar-pipeline
tipo: feature | sp: 2 | prioridade: alta | status: ✅
depende de: NPBB-F3-01-001
Descrição:
Criar endpoint que valida que o lote está em stage=silver e dispara a função
de pipeline como background task. Retorna imediatamente com status=queued.
Critérios de Aceitação:

 Retorna 400 se lote não está em stage=silver
 Retorna 401 sem JWT
 Retorna {batch_id, status: "queued"} imediatamente
 Pipeline executa em background (não bloqueia resposta)
 GET /leads/batches/{id} reflete o status atualizado após conclusão

Tarefas:

 T1: Criar rota POST /leads/batches/{id}/executar-pipeline com BackgroundTasks
 T2: Validar stage=silver antes de enfileirar
 T3: Garantir que GET /leads/batches/{id} existe e retorna stage + pipeline_status
 T4: Pytest (lote silver → queued OK; lote bronze → 400; sem JWT → 401)


NPBB-F3-01-003 — UI de Status do Pipeline e Relatório
tipo: feature | sp: 3 | prioridade: alta | status: ✅
depende de: NPBB-F3-01-002
Descrição:
Criar página (ou modal) de acompanhamento do lote que exibe: stage atual,
pipeline_status, métricas do relatório (raw_rows, valid_rows, discarded_rows,
quality_metrics) e lista de fail_reasons se FAIL. Inclui botão "Executar Pipeline"
(chama o endpoint) e polling de status enquanto pipeline_status=queued.
Critérios de Aceitação:

 Exibe stage, pipeline_status e métricas principais
 Polling a cada 3s enquanto status=queued (para quando status != queued)
 PASS/PASS_WITH_WARNINGS: exibe contagem de leads Gold promovidos
 FAIL: exibe lista de fail_reasons em destaque
 Botão "Executar Pipeline" visível apenas quando stage=silver

Tarefas:

 T1: Criar frontend/src/pages/leads/PipelineStatusPage.tsx
 T2: Polling com setInterval + limpeza no useEffect cleanup
 T3: Componente de métricas (raw/valid/discarded + quality_metrics)
 T4: Seção de fail_reasons com MUI Alert severity=error
 T5: Integrar botão "Executar Pipeline" com chamada ao endpoint