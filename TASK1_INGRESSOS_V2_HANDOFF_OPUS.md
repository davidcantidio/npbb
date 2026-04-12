# Handoff Task 1: Ingressos v2

Contexto de revisão para o Opus frente a [plan.md](plan.md).

## Objetivo

Revisar a implementação da Task 1 do domínio de ingressos v2 no backend do NPBB, verificando aderência ao `plan.md`, consistência de modelo/migration e possíveis correções antes de avançar para Tasks 2+.

## Arquivos alterados nesta implementação

- [backend/app/models/ingressos_v2_models.py](/c:/Users/NPBB/npbb/backend/app/models/ingressos_v2_models.py)
- [backend/alembic/versions/4c7a9d2e1f3b_add_ingressos_v2_inventory_and_receipts.py](/c:/Users/NPBB/npbb/backend/alembic/versions/4c7a9d2e1f3b_add_ingressos_v2_inventory_and_receipts.py)
- [backend/app/models/__init__.py](/c:/Users/NPBB/npbb/backend/app/models/__init__.py)
- [backend/alembic/env.py](/c:/Users/NPBB/npbb/backend/alembic/env.py)
- [backend/app/models/models.py](/c:/Users/NPBB/npbb/backend/app/models/models.py)

## Escopo implementado

A implementação consolidou a Task 1 como backend-only, sem adicionar novos serviços de negócio, reconciliação, emails, PDF ou novos endpoints além dos artefatos v2 que já existiam no repositório.

Foram mantidos:

- enums centralizados em `backend/app/models/models.py`
- legado `cota_cortesia` e `solicitacao_ingresso` intocados
- `backend/app/models/ingressos_v2_models.py` como módulo único dos modelos v2

## O que foi implementado

### Enums

Mantidos em `backend/app/models/models.py`:

- `TipoIngresso`
- `ModoFornecimento`
- `StatusInventario`
- `StatusDestinatario`
- `TipoAjuste`
- `TipoOcorrencia`

### Modelos em `ingressos_v2_models.py`

Modelos presentes e consolidados:

- `ConfiguracaoIngressoEvento`
- `ConfiguracaoIngressoEventoTipo`
- `PrevisaoIngresso`
- `RecebimentoIngresso`
- `InventarioIngresso`
- `DistribuicaoIngresso`
- `AjusteIngresso`
- `OcorrenciaIngresso`
- `AuditoriaIngressoEvento`

### Regras de schema aplicadas

- `PrevisaoIngresso`
  - unique natural key em `(evento_id, diretoria_id, tipo_ingresso)`
  - `quantidade >= 0`
  - relationships mínimos com `Evento` e `Diretoria`

- `RecebimentoIngresso`
  - histórico append-only
  - `quantidade > 0`
  - campos `artifact_file_path`, `artifact_link`, `artifact_instructions`
  - `correlation_id` obrigatório com `default_factory` UUID string
  - relationships mínimos com `Evento` e `Diretoria`

- `InventarioIngresso`
  - snapshot materializado
  - unique em `(evento_id, diretoria_id, tipo_ingresso)`
  - contadores `planejado`, `recebido_confirmado`, `bloqueado`, `disponivel`, `distribuido`
  - todos com checks `>= 0`
  - comentário curto no modelo indicando que a reconciliação futura será a escritora

- `DistribuicaoIngresso`
  - `qr_uuid` único com UUID4 string
  - `correlation_id` obrigatório com UUID4 string
  - timestamps de ciclo de vida
  - checks simples para nome/email não vazios
  - relationships mínimos com `Evento` e `Diretoria`

- `AjusteIngresso`
  - `quantidade > 0`
  - `correlation_id` obrigatório com UUID4 string
  - origem/destino nullable
  - relationship mínimo com `Evento`

- `OcorrenciaIngresso`
  - event-scoped incident com `tipo_canonico`, `descricao`, `usuario_id`
  - relationships mínimos com `Evento` e `Diretoria`

- `AuditoriaIngressoEvento`
  - append-only log com `modo_fornecimento_anterior`, `modo_fornecimento_novo`, `usuario_id`
  - mantido `updated_at` por consistência com o restante do v2
  - relationship mínimo com `Evento`

## Migration implementada

Revisão:

- [backend/alembic/versions/4c7a9d2e1f3b_add_ingressos_v2_inventory_and_receipts.py](/c:/Users/NPBB/npbb/backend/alembic/versions/4c7a9d2e1f3b_add_ingressos_v2_inventory_and_receipts.py)

Ela foi ampliada para cobrir defensivamente as tabelas faltantes da Task 1:

- `recebimento_ingresso`
- `inventario_ingresso`
- `distribuicao_ingresso`
- `ajuste_ingresso`
- `ocorrencia_ingresso`
- `auditoria_ingresso_evento`

Ela reaproveita a chain já existente para:

- `configuracao_ingresso_evento`
- `configuracao_ingresso_evento_tipo`
- `previsao_ingresso`

Também adiciona criação defensiva dos enums Postgres faltantes:

- `statusdestinatario`
- `tipoajuste`
- `tipoocorrencia`

Sem alterar:

- `cota_cortesia`
- `solicitacao_ingresso`

## Wiring / metadata

Para evitar ciclo de import:

- removi a reexportação dos modelos v2 em `backend/app/models/models.py`
- registrei o módulo v2 no bootstrap de metadata em:
  - [backend/app/models/__init__.py](/c:/Users/NPBB/npbb/backend/app/models/__init__.py)
  - [backend/alembic/env.py](/c:/Users/NPBB/npbb/backend/alembic/env.py)

## Verificações executadas

Passaram:

- import direto dos modelos v2
- import do router existente `app.routers.ingressos_v2`
- `SQLModel.metadata.create_all()` com SQLite
- ciclo `alembic upgrade head -> downgrade -1 -> upgrade head`

Não executei com sucesso:

- `backend/tests/test_ingressos_v2_endpoints.py`

Motivo:

- o ambiente local quebra antes por falta de `pandas` na subida do app principal, então a falha observada parece ser de ambiente e não diretamente da Task 1

## Pontos que quero que o Opus revise

1. Aderência exata da implementação à Task 1 do `plan.md`, dado que o repo já tinha artefatos de começo de Task 2.
2. Se `AuditoriaIngressoEvento` deve manter `updated_at` ou virar tabela append-only só com `created_at`.
3. Se `StatusInventario` deve continuar apenas em código, já que o snapshot atual não persiste esse enum em coluna.
4. Se os `correlation_id` obrigatórios em `DistribuicaoIngresso` e `AjusteIngresso` estão alinhados com a intenção do plano.
5. Se vale endurecer já no schema as regras de origem/destino por `TipoAjuste`, ou deixar isso para serviços futuros.
6. Se os constraints e nomes físicos de índices/uniques estão consistentes com a convenção do projeto.
7. Se o `downgrade` da revisão está seguro ao dropar os enums criados nessa mesma revisão.
8. Se faltam relationships mínimos adicionais para `Usuario`, `Diretoria` ou `ConfiguracaoIngressoEventoTipo`.
9. Se existe qualquer divergência importante entre o snapshot materializado de `InventarioIngresso` e a descrição da Task 3, que mereça ajuste já agora.

## Resultado esperado da revisão do Opus

Peço uma revisão crítica com foco em:

- bugs de schema
- riscos de migration
- incompatibilidades com `plan.md`
- regressões potenciais
- correções pontuais recomendadas antes de seguir para Task 2
