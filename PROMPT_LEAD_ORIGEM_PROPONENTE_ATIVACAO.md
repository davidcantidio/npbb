# Prompt de implementação — origem de lead (proponente vs. ativação)

## Contexto

No produto, um lead ligado a um evento deve refletir claramente duas origens conceituais:

1. **Proponente** — quando o tipo de lead é **`entrada_evento`** ou **`bilheteria`** (tratar ambos como responsabilidade do proponente no domínio de negócio).
2. **Ativação** — quando o lead **converteu no contexto de uma ativação** (fluxo com `ativacao` / vínculo `ativacao_lead` / `source_kind` de ativação, conforme o código atual).

Hoje já existem tabelas/campos relevantes:

- `lead_evento`: `tipo_lead` (`bilheteria` | `entrada_evento` | `ativacao`), `responsavel_tipo` (`proponente` | `agencia`), `source_kind`, `source_ref_id`, etc. (ver `backend/app/models/lead_public_models.py` e migration `f5e6d7c8b9a0_add_lead_origin_attributes.py`).
- `ativacao_lead`: vínculo lead ↔ ativação.
- O submit público em `backend/app/services/landing_page_submission.py` define `_lead_event_origin_kwargs` (sem ativação → `entrada_evento`; com ativação + agência → `ativacao` + `agencia`).

## Objetivo

Estabelecer no **banco de dados** (e de forma consistente na **aplicação**) que:

- **`tipo_lead IN ('entrada_evento', 'bilheteria')` implica origem “proponente”**: persistir isso de forma explícita, preferencialmente com `responsavel_tipo = 'proponente'` e regras de consistência (e `responsavel_agencia_id` NULL, alinhado aos checks existentes).
- **Lead que converteu em ativação** fique inequívoco: além de `tipo_lead = 'ativacao'` quando aplicável, garantir coerência com `source_kind`, presença de `ativacao_lead` quando o fluxo for de ativação, e com as constraints atuais (ex.: quando `tipo_lead = 'ativacao'`, o check atual exige `responsavel_tipo = 'agencia'` — não quebrar isso; se a regra de negócio for “ativação = agência executora”, documentar e manter; se precisar de outro significado, propor evolução do modelo em vez de violar constraints).

## Tarefas

### 1. Especificação de dados

- Documentar a matriz decisória: `(tipo_lead, source_kind, presença de ativacao_lead)` → o que o sistema grava e o que o dashboard/report espera.
- Definir se “proponente” será **sempre** `responsavel_tipo = 'proponente'` para `bilheteria` e `entrada_evento`, e qual campo preenche “quem é o proponente” (ex.: `responsavel_nome` com nome do evento, gestor, diretoria, etc.) — escolher uma fonte canônica e justificar.

### 2. Migrations / constraints

- Adicionar constraints ou triggers (Postgres) que **garantam** a consistência, por exemplo:
  - Se `tipo_lead` é `entrada_evento` ou `bilheteria`, então `responsavel_tipo` deve ser `proponente` e `responsavel_agencia_id` IS NULL (compatível com `ck_lead_evento_responsavel_agencia_consistency`).
  - Ajustar ou complementar checks existentes sem conflitar com `ck_lead_evento_tipo_lead_ativacao_agencia`.
- Se necessário, relaxar ou refatorar checks antigos apenas com **plano de migração de dados** primeiro.

### 3. Backfill

- Script de migração de dados (no `upgrade()` ou job separado) para linhas existentes em `lead_evento` onde `tipo_lead` é `entrada_evento` ou `bilheteria` mas `responsavel_tipo` está NULL: preencher `proponente` e `responsavel_nome` segundo a regra escolhida.
- Validar contagens antes/depois e casos ambíguos (NULLs).

### 4. Código da aplicação

- Atualizar `_lead_event_origin_kwargs` e qualquer outro caminho que cria/atualiza `lead_evento` (`ensure_lead_event`, imports, bilheteria, etc.) para **sempre** gravar `responsavel_tipo`/`responsavel_nome` alinhados à nova regra.
- Garantir que conversão em ativação continue criando/atualizando `ativacao_lead` e `lead_evento` com `source_kind` correto.

### 5. Testes

- Testes de modelo/migration (SQLite + Postgres se o projeto roda ambos).
- Testes de serviço cobrindo: submit landing sem ativação; com ativação; import/bilheteria se existir fluxo.

### 6. Critérios de aceite

- Nenhuma linha nova de `lead_evento` com `tipo_lead` em `entrada_evento`/`bilheteria` sem `responsavel_tipo = 'proponente'` (ou política explícita documentada).
- Leads de ativação continuam distinguíveis e consultáveis.
- `alembic upgrade head` aplica sem erro; downgrade definido se for política do time.

## Restrições

- Mudanças mínimas e focadas; seguir estilo do repositório.
- Não remover dados sem estratégia de backfill.
- Responder em português nos commits/comentários se for padrão do time.
