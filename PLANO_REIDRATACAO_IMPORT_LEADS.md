# Reidratação de Metadados no Reenvio de Arquivo de Leads

## Summary
- Adicionar um hint read-only para importar novamente um ficheiro já visto e pré-preencher o Bronze com a última configuração válida do mesmo utilizador.
- Manter `POST /leads/batches` inalterado; a reidratação é opt-in no cliente e não interfere no resume Gold nem nas sugestões Silver.
- Este documento serve como contrato para o agente implementador.

## Functional Requirements
- When o utilizador selecionar um ficheiro no fluxo Bronze, o frontend shall calcular `SHA-256` dos bytes no browser e consultar `GET /leads/batches/import-hint?arquivo_sha256=<64_hex>`.
- When existir um `LeadBatch` do mesmo `enviado_por` com o mesmo `arquivo_sha256`, o backend shall devolver `200` com `arquivo_sha256`, `source_batch_id`, `plataforma_origem`, `data_envio`, `origem_lote`, `tipo_lead_proponente`, `evento_id`, `ativacao_id`, `confidence: "exact_hash_match"` e `source_created_at`.
- When não existir match, o backend shall devolver `204 No Content`.
- When o hash for inválido, o backend shall devolver `400` estruturado via `raise_http_error`; a validação deve ser manual no handler para evitar `422` automático do FastAPI.
- When houver múltiplos lotes com o mesmo hash para o mesmo utilizador, o backend shall usar o mais recente por `created_at DESC, id DESC`.
- When o hint chegar depois de o utilizador editar o formulário, o frontend shall aplicar o hint só uma vez por ficheiro/hash e nunca sobrescrever campos já marcados como editados manualmente.
- When o hint referir `ativacao_id`, o frontend shall aplicar `evento_id`/`origem_lote` primeiro e só selecionar a ativação depois do load das ativações, para não perder o valor com os resets já existentes.
- Where o catálogo atual já não suportar o metadado reidratado, o sistema shall manter a validação atual e permitir correção manual sem bloquear o upload.
- The sistema shall filtrar sempre por `enviado_por`, não devolver `arquivo_bronze` nem PII, e falhar em modo best effort: erro no hash/hint nunca impede o fluxo manual.

## Implementation Checklist
- Backend
  - Adicionar schema de resposta de hint em `backend/app/schemas/lead_batch.py`.
  - Adicionar endpoint em `backend/app/routers/leads.py` com query por `LeadBatch.arquivo_sha256` + `LeadBatch.enviado_por == current_user.id`, `limit(1)` e ordenação por recência.
  - Normalizar hash para lowercase e ignorar linhas antigas com `arquivo_sha256 = NULL`.
- Frontend shared
  - Adicionar `getLeadImportMetadataHint(token, arquivoSha256): Promise<LeadImportMetadataHint | null>` em `frontend/src/services/leads_import.ts`.
  - Adicionar helper compartilhado `File -> sha256 hex` via `crypto.subtle.digest`.
  - Adicionar helper para normalizar `data_envio` do backend para `YYYY-MM-DD` do `input[type="date"]`.
- Fluxo Bronze single
  - Em `ImportacaoPage.tsx`, no `handleSelectFile`, resetar estado de hint anterior, calcular hash, pedir hint e ignorar respostas stale por `requestId`.
  - Rastrear dirty fields para `plataforma_origem`, `data_envio`, `bronzeEventoId`, `bronzeOrigemLote`, `bronzeTipoLeadProponente` e `bronzeAtivacaoId`.
  - Aplicar hint em duas etapas para lotes de ativação e mostrar `Alert` informativo no upload step.
- Fluxo Bronze batch
  - Estender `BatchUploadRowDraft` com estado local de reidratação, no mínimo dirty fields, mensagem informativa e `pending_hint_ativacao_id`.
  - Em `useBatchUploadDraft.ts`, após `addFiles`, hidratar as novas linhas em background com concorrência limitada e aplicar hint apenas a campos não editados.
  - Aplicar `ativacao_id` em segundo passo após o carregamento das ativações da linha.
  - Exibir feedback por linha usando o grid atual, sem transformar falha de hint em erro de validação.
- Documento de handoff
  - Manter este `PLANO_REIDRATACAO_IMPORT_LEADS.md` na raiz como especificação viva da feature.

## Error Handling and Acceptance
| Cenário | Resultado esperado |
| --- | --- |
| `arquivo_sha256` malformado | `400` com código/mensagem estruturados |
| Hash sem histórico | `204`; UI mantém defaults atuais |
| Mesmo hash, outro utilizador | `204`; nenhum vazamento |
| Falha ao calcular hash ou consultar hint | UI ignora a feature opcional e mantém upload manual funcional |
| Evento/ativação do hint não disponíveis hoje | UI mantém guardrails atuais e permite ajuste manual |

## Test Plan
- Given dois batches do mesmo utilizador com o mesmo hash, When consultar o hint, Then a API devolve o lote mais recente.
- Given nenhum batch com o hash para o utilizador autenticado, When consultar o hint, Then a API devolve `204`.
- Given batch de outro utilizador com o mesmo hash, When consultar o hint, Then a API não devolve dados.
- Given hash inválido, When consultar o hint, Then a API devolve `400` e não `422`.
- Given um ficheiro já importado no Bronze single, When o utilizador o seleciona de novo, Then a UI reidrata plataforma/data/evento/origem/tipo e, se aplicável, a ativação depois do load das opções.
- Given o utilizador edita campos antes do hint resolver, When o hint chega, Then esses campos manuais permanecem intactos.
- Given múltiplos ficheiros no batch mode, When alguns têm histórico e outros não, Then cada linha é reidratada independentemente e as linhas sem histórico ficam nos defaults.
- Given lotes antigos com `arquivo_sha256 = NULL`, When o utilizador reenviar o ficheiro, Then não há erro e não há reidratação.

## Assumptions and Defaults
- Contrato escolhido: `GET` com query param e `204` em no-match.
- Política escolhida: aplicar hint uma única vez por ficheiro/hash e preservar edits manuais.
- A chave de matching é exclusivamente `SHA-256(bytes)`; o nome do ficheiro não participa.
- Não haverá backfill/migração neste MVP; lotes antigos sem hash continuam fora da funcionalidade.
- O comportamento atual de `POST /leads/batches`, resume Gold e aliases Silver permanece fora de âmbito.
