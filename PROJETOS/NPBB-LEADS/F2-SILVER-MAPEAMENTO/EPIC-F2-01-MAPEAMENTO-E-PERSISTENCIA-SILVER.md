EPIC-F2-01 — Mapeamento de Colunas e Persistência Silver
projeto: NPBB-LEADS | fase: F2 | status: 🔲
depende de: F1 concluída (batch_id disponível, arquivo bronze no banco)

1. Resumo
Permitir que o operador mapeie as colunas do arquivo bruto para os campos
canônicos do banco, vinculando o lote a um evento. O sistema sugere mapeamentos
automaticamente usando HEADER_SYNONYMS de constants.py e aliases salvos
de envios anteriores. Após confirmação, persiste os dados brutos mapeados em
leads_silver e salva os aliases para reuso futuro.
2. Contexto Arquitetural

PROJETOS/lead_pipeline/constants.py — HEADER_SYNONYMS: base das sugestões automáticas
PROJETOS/lead_pipeline/normalization.py — normalize_header(): lógica de canonicalização
Modelos criados no F1: LeadBatch, LeadColumnAlias, LeadSilver
Campos canônicos: nome, cpf, data_nascimento, email, telefone, evento,
tipo_evento, local, data_evento

3. Riscos

Colunas com mesmo nome em aliases de plataformas diferentes não devem conflitar
Não executar normalização de dados aqui — Silver preserva o dado bruto
Não executar o pipeline Gold aqui — apenas persistir o Silver e atualizar o stage

4. Definition of Done

 Endpoint GET /leads/batches/{id}/colunas retorna colunas + sugestões de mapeamento
 Sugestão automática baseada em HEADER_SYNONYMS + aliases salvos por plataforma
 POST /leads/batches/{id}/mapear persiste o mapeamento, cria leads_silver, salva aliases
 Stage do lote atualizado para silver
 UI de mapeamento funcional com confirmação do operador
 CI verde sem regressão


Issues
NPBB-F2-01-001 — Endpoint de Sugestão de Mapeamento
tipo: feature | sp: 3 | prioridade: alta | status: 🔲
depende de: NPBB-F1-01-001 (modelos), NPBB-F1-02-002 (preview endpoint)
Descrição:
Criar GET /leads/batches/{id}/colunas que lê o arquivo bronze do lote, detecta
as colunas presentes, e para cada coluna retorna: nome original, sugestão de
campo canônico (de HEADER_SYNONYMS + aliases salvos para a plataforma_origem
do lote), e confiança da sugestão (exact_match / synonym_match / alias_match / none).
Critérios de Aceitação:

 Retorna lista de {coluna_original, campo_sugerido, confiança} para cada coluna
 Sugestão usa HEADER_SYNONYMS do lead_pipeline (sem duplicar a lógica — importar de lá)
 Sugestão usa aliases salvos filtrados por plataforma_origem do lote
 Colunas sem sugestão retornam campo_sugerido: null, confiança: none

Tarefas:

 T1: Criar serviço backend/app/services/lead_mapping.py
com função suggest_column_mapping(batch_id, db) -> list[ColumnSuggestion]
 T2: Importar HEADER_SYNONYMS e normalize_header de lead_pipeline
via PYTHONPATH (não copiar o código)
 T3: Consultar lead_column_aliases filtrando por plataforma_origem
 T4: Criar rota GET /leads/batches/{id}/colunas
 T5: Teste pytest (com/sem aliases salvos, com sinônimos conhecidos)

Notas técnicas:
Importar direto: from lead_pipeline.constants import HEADER_SYNONYMS
e from lead_pipeline.normalization import normalize_header — o PYTHONPATH
já inclui o raiz do repo.

NPBB-F2-01-002 — Endpoint de Confirmação do Mapeamento + Persistência Silver
tipo: feature | sp: 5 | prioridade: alta | status: 🔲
depende de: NPBB-F2-01-001
Descrição:
Criar POST /leads/batches/{id}/mapear que recebe o mapeamento confirmado pelo
operador (dict coluna_original → campo_canônico) e o evento_id. Persiste cada
linha do arquivo em leads_silver como dados_brutos (jsonb com chaves
canônicas), salva os novos aliases, atualiza batch stage para silver.
Critérios de Aceitação:

 Aceita body: {evento_id, mapeamento: {coluna_original: campo_canonico}}
 Cria 1 registro em leads_silver por linha do arquivo
 dados_brutos contém as colunas mapeadas com chaves canônicas
 Aliases novos (não existentes para a plataforma) são salvos em lead_column_aliases
 lead_batches.stage atualizado para silver
 lead_batches.evento_id atualizado
 Retorna {batch_id, silver_count, stage: "silver"}
 Retorna 401 sem JWT

Tarefas:

 T1: Criar rota POST /leads/batches/{id}/mapear
 T2: Ler arquivo bronze, aplicar mapeamento, criar registros LeadSilver
 T3: Salvar aliases novos em LeadColumnAlias (upsert por coluna+plataforma)
 T4: Atualizar LeadBatch.stage = "silver" e evento_id
 T5: Escrever pytest (mapeamento completo, mapeamento parcial, sem JWT → 401)


NPBB-F2-01-003 — UI de Mapeamento de Colunas
tipo: feature | sp: 3 | prioridade: alta | status: 🔲
depende de: NPBB-F2-01-001, NPBB-F2-01-002
Descrição:
Criar página de mapeamento que o operador acessa após o Step 2 do upload.
Exibe uma tabela com: coluna original, sugestão automática (select pré-preenchido),
campo canônico final (editável). Operador escolhe o evento de referência e confirma.
Critérios de Aceitação:

 Página acessível via /leads/importar/mapear?batch_id=<id>
 Carrega sugestões via GET /leads/batches/{id}/colunas
 Select de evento carregado da API de eventos existente
 Operador pode sobrescrever qualquer sugestão
 Botão "Confirmar Mapeamento" chama POST /leads/batches/{id}/mapear
 Após sucesso, exibe contagem de leads Silver e botão "Executar Pipeline"

Tarefas:

 T1: Criar frontend/src/pages/leads/MapeamentoPage.tsx
 T2: Tabela de mapeamento com select por linha (MUI Select)
 T3: Select de evento (reutilizar componente existente se houver)
 T4: Chamada POST ao confirmar + navegação para status do pipeline

