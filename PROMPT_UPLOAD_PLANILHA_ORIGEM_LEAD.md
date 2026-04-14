# Prompt de implementação — upload de planilha (origem proponente vs ativação)

Documento de especificação para implementação no repositório. Relacionado a [PROMPT_LEAD_ORIGEM_PROPONENTE_ATIVACAO.md](PROMPT_LEAD_ORIGEM_PROPONENTE_ATIVACAO.md) (se existir).

## Decisão de produto (confirmada)

- **Proponente** e **Ativação** são escolhas mutuamente exclusivas no primeiro passo (upload Bronze).
- Se **Ativação**: **obrigar** o operador a selecionar uma **ativação** pertencente ao **mesmo evento** já escolhido no upload.
- Se o evento **não tiver nenhuma ativação**: permitir **criar uma ativação ad hoc** (fluxo mínimo: nome + defaults), depois selecioná-la — reutilizando contratos existentes ([`frontend/src/services/eventos/workflow.ts`](frontend/src/services/eventos/workflow.ts) `createEventoAtivacao` e backend em [`backend/app/routers/eventos/ativacoes.py`](backend/app/routers/eventos/ativacoes.py) / [`backend/app/routers/ativacao.py`](backend/app/routers/ativacao.py)).

## Contexto técnico no repo (para o implementador)

- Tela e estado do fluxo: [`frontend/src/pages/leads/ImportacaoPage.tsx`](frontend/src/pages/leads/ImportacaoPage.tsx) + formulário Bronze em [`frontend/src/pages/leads/importacao/ImportacaoUploadStep.tsx`](frontend/src/pages/leads/importacao/ImportacaoUploadStep.tsx).
- Cliente HTTP: `createLeadBatch` em [`frontend/src/services/leads_import.ts`](frontend/src/services/leads_import.ts) (`FormData` para `POST /leads/batches`).
- API de criação de lote: `criar_batch` em [`backend/app/routers/leads.py`](backend/app/routers/leads.py) (~linha 1407).
- Modelo de lote: [`backend/app/models/lead_batch.py`](backend/app/models/lead_batch.py) (`LeadBatch`) — hoje não persiste origem nem `ativacao_id`.
- Ligação lead↔evento pós-pipeline: [`backend/app/services/lead_pipeline_service.py`](backend/app/services/lead_pipeline_service.py) chama `ensure_lead_event` com `LeadEventoSourceKind.LEAD_BATCH`. A canonicalização em [`backend/app/services/lead_event_service.py`](backend/app/services/lead_event_service.py) (`_derive_canonical_lead_origin`) trata **ACTIVATION** (exige `AtivacaoLead` em `source_ref_id`) vs demais fontes (proponente + `entrada_evento`/`bilheteria`). Para alinhar “lote = ativação” com o modelo atual, o pipeline precisará **criar ou reutilizar `AtivacaoLead`** por lead e chamar `ensure_lead_event` com **`ACTIVATION`** e `source_ref_id=ativacao_lead.id` (detalhe de implementação obrigatório no prompt).

## 1. Objetivo

No passo inicial **Upload** do fluxo `/leads/importar` (Bronze), adicionar controles para o operador declarar se o lote é de **Proponente** ou de **Ativação**, persistir isso no backend e refletir corretamente em **`lead_evento`** (e vínculos **`ativacao_lead`** quando for ativação), alinhado a [PROMPT_LEAD_ORIGEM_PROPONENTE_ATIVACAO.md](PROMPT_LEAD_ORIGEM_PROPONENTE_ATIVACAO.md) se já existir no repo.

## 2. UX — Proponente

- Controle claro (ex.: radio ou segmented control): **Proponente**.
- Sub-opção se necessário para o pipeline/canonicalização: **`bilheteria`** vs **`entrada_evento`** (valores alinhados a `TipoLead`), ou um único default documentado.
- `canSubmit` só habilita envio com arquivo + evento + metadados obrigatórios atuais + nova origem válida.

## 3. UX — Ativação

- Controle: **Ativação**.
- **Autocomplete ou select** de ativações filtradas por `evento_id` selecionado no mesmo formulário.
- **Validação**: se origem = Ativação e não há `ativacao_id`, bloquear submit com mensagem clara.
- **Lista vazia**: exibir estado vazio com ação **“Criar ativação para este evento”** (modal ou painel) com formulário mínimo (ex.: nome obrigatório); ao sucesso, atualizar lista e **pré-selecionar** a ativação criada. Usar `createEventoAtivacao` / endpoint já existente; não duplicar contrato sem necessidade.

## 4. Backend — persistência do lote

- Migration: novos campos em `lead_batches` (nomes sugeridos a definir pelo implementador, ex.: `origem_lote` enum `proponente|ativacao`, `tipo_lead_proponente` opcional, `ativacao_id` obrigatório quando `origem_lote=ativacao`).
- `POST /leads/batches`: aceitar novos campos `Form` (validar coerência `ativacao.evento_id == evento_id` do lote).
- `LeadBatchRead` / OpenAPI: expor campos para o front exibir resumo no [`BatchSummaryCard`](frontend/src/pages/leads/importacao/BatchSummaryCard.tsx) se fizer sentido.

## 5. Pipeline / Gold

- Ao materializar leads com `batch.evento_id` e origem **Proponente**: manter `LEAD_BATCH` mas passar `tipo_lead` explícito (`bilheteria` ou `entrada_evento`) para `ensure_lead_event` se a canonicalização depender disso (ver `_derive_canonical_lead_origin`).
- Ao materializar com origem **Ativação**: para cada lead promovido com `batch.ativacao_id`, garantir registro em **`ativacao_lead`** (par único `ativacao_id`+`lead_id`) e em seguida `ensure_lead_event(..., source_kind=ACTIVATION, source_ref_id=<ativacao_lead.id>)`. Tratar idempotência e concorrência (unique constraint já existe em `ativacao_lead`).

## 6. Testes

- Front: estender [`frontend/src/pages/__tests__/ImportacaoPage.test.tsx`](frontend/src/pages/__tests__/ImportacaoPage.test.tsx) — payload de `createLeadBatch` inclui novos campos; fluxo ativação bloqueado sem seleção; mock de criação de ativação quando lista vazia.
- Back: testes de rota `criar_batch` + testes de pipeline (`test_lead_gold_pipeline.py` ou equivalente) cobrindo os dois modos.

## 7. Critérios de aceite

- Impossível enviar lote “Ativação” sem `ativacao_id` válido do evento.
- Evento sem ativações: usuário consegue criar ad hoc e concluir upload na mesma sessão.
- Leads promovidos refletem `lead_evento` coerente (proponente vs ativação conforme regras do serviço de canonicalização).

## Nota operacional

Antes de aplicar patches em ambiente compartilhado, confirmar o root do repositório (`npbb`) caso o workspace do editor aponte para outro diretório.
