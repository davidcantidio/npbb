# Handoff - Task 3: Reconciliacao, Inventario e Desbloqueio Manual (Ingressos v2)

Documento para o Opus revisar, auditar e corrigir a implementacao da Task 3 do [`plan.md`](plan.md).

## Objetivo do escopo

Completar a Task 3 do dominio de ingressos v2 no backend do NPBB:

1. registrar recebimentos externos
2. expor snapshots de inventario materializado
3. suportar desbloqueio manual persistente e auditado
4. manter o snapshot estavel em recalculos posteriores

Fora de escopo:

- Task 4 (distribuicoes / lifecycle)
- Task 10 (OpenClaw), exceto suporte a `correlation_id`
- validacao obrigatoria de artefatos de recebimento em v1

## Ficheiros principais

1. [backend/app/services/inventario_ingressos.py](backend/app/services/inventario_ingressos.py)
2. [backend/app/routers/ingressos_v2.py](backend/app/routers/ingressos_v2.py)
3. [backend/app/models/ingressos_v2_models.py](backend/app/models/ingressos_v2_models.py)
4. [backend/app/schemas/ingressos_v2.py](backend/app/schemas/ingressos_v2.py)
5. [backend/alembic/versions/4c7a9d2e1f3b_add_ingressos_v2_inventory_and_receipts.py](backend/alembic/versions/4c7a9d2e1f3b_add_ingressos_v2_inventory_and_receipts.py)
6. [backend/tests/test_inventario_ingressos_service.py](backend/tests/test_inventario_ingressos_service.py)
7. [backend/tests/test_ingressos_v2_endpoints.py](backend/tests/test_ingressos_v2_endpoints.py)
8. [backend/app/models/models.py](backend/app/models/models.py)

## Decisao de design implementada

Foi escolhida a abordagem A do prompt:

- `AuditoriaDesbloqueioInventario` como trilha append-only especifica para override manual
- `DesbloqueioManualInventario` como estado persistido do override ativo por `(evento, diretoria, tipo)`

Nao foi reutilizado `AuditoriaIngressoEvento` nem `OcorrenciaIngresso`.

Tambem foi adicionado o enum de dominio `TipoBloqueioInventario` com:

- `falta_recebimento`
- `excesso_recebido`

## Invariantes da reconciliacao

O snapshot continua a ser o writer canonico do estado em `InventarioIngresso`.

Para `modo_fornecimento = externo_recebido`:

- bloqueio base por falta: `max(planejado - recebido_confirmado, 0)`
- bloqueio base por excesso: `max(recebido_confirmado - planejado, 0)`
- so um tipo de bloqueio base e valido por vez
- o desbloqueio manual so e aplicado quando o override persistido coincide com o tipo de bloqueio base atual
- a quantidade efetiva libertada e `min(quantidade_restante, bloqueio_base_atual)`
- `bloqueado = bloqueio_base - quantidade_efetiva`
- `disponivel = max(min(recebido_confirmado, planejado) + quantidade_efetiva - distribuido, 0)`

Regras de estabilidade implementadas:

- se o evento muda para modo interno, o override manual ativo e apagado
- se o bloqueio natural desaparece, o override manual ativo e apagado
- se o tipo de bloqueio muda, o override manual ativo e apagado
- se o bloqueio natural diminui, `quantidade_restante` e capada ao novo maximo ainda aplicavel

Isto evita que override antigo sobreviva quando o contexto deixa de existir. O ponto mais importante para auditoria do Opus e validar se este comportamento bate exatamente com a expectativa de produto para "nao ressuscitar" credito antigo.

## API HTTP implementada

### POST `/ingressos/v2/eventos/{evento_id}/recebimentos`

- auth: `require_npbb_user`
- body: `diretoria_id`, `tipo_ingresso`, `quantidade`, artefatos opcionais, `correlation_id` opcional
- resposta: `{ recebimento, inventario }`
- codigos relevantes:
  - `404 CONFIGURACAO_INGRESSO_NOT_FOUND`
  - `400 TIPO_INGRESSO_INVALID_FOR_EVENT`
  - `400 RECEBIMENTO_INVALID_MODE`
  - `400 RECEBIMENTO_QUANTIDADE_INVALIDA`

### GET `/ingressos/v2/eventos/{evento_id}/inventario`

- auth: `get_current_user`
- query params opcionais: `diretoria_id`, `tipo_ingresso`
- le apenas o snapshot materializado; nao força recalculo por padrao
- exige visibilidade do evento e configuracao existente

### POST `/ingressos/v2/eventos/{evento_id}/inventario/desbloqueio-manual`

- auth: `require_npbb_user`
- body: `diretoria_id`, `tipo_ingresso`, `quantidade` opcional, `motivo`, `correlation_id` opcional
- resposta: metadados da auditoria + `inventario`
- codigos relevantes:
  - `400 DESBLOQUEIO_MANUAL_INVALID_MODE`
  - `400 DESBLOQUEIO_MANUAL_QUANTIDADE_INVALIDA`
  - `400 DESBLOQUEIO_MANUAL_MOTIVO_OBRIGATORIO`
  - `409 DESBLOQUEIO_MANUAL_SEM_BLOQUEIO`
  - `409 DESBLOQUEIO_MANUAL_EXCEDE_BLOQUEIO`

## Escopo concretamente implementado

### Modelagem

- `TipoBloqueioInventario` em `backend/app/models/models.py`
- `DesbloqueioManualInventario`
- `AuditoriaDesbloqueioInventario`

### Servico

- `registrar_recebimento()` mantido e integrado aos novos schemas/endpoints
- `calcular_inventario()` agora aplica override manual persistido
- `desbloqueio_manual()` novo fluxo de admin override com auditoria

### Router / Schemas

- novos schemas:
  - `RecebimentoIngressoCreate`
  - `RecebimentoIngressoRead`
  - `InventarioIngressoRead`
  - `RecebimentoIngressoResponse`
  - `DesbloqueioManualInventarioCreate`
  - `DesbloqueioManualInventarioResponse`
- traducao de `ValueError` do servico via `raise_http_error()`

### Migration

A revision existente `4c7a9d2e1f3b` foi expandida para incluir:

- enum `tipobloqueioinventario`
- tabela `desbloqueio_manual_inventario`
- tabela `auditoria_desbloqueio_inventario`

## Testes executados

Executados localmente com `PYTHONPATH` configurado:

```powershell
$env:PYTHONPATH='c:/Users/NPBB/npbb;c:/Users/NPBB/npbb/backend'
$env:SECRET_KEY='ci-secret-key'
$env:TESTING='true'
& 'c:/Users/NPBB/npbb/backend/.venv/Scripts/python.exe' -m pytest tests/test_inventario_ingressos_service.py -q -p no:cacheprovider
& 'c:/Users/NPBB/npbb/backend/.venv/Scripts/python.exe' -m pytest tests/test_ingressos_v2_endpoints.py -q -p no:cacheprovider
```

Resultado observado:

- `tests/test_inventario_ingressos_service.py`: `22 passed`
- `tests/test_ingressos_v2_endpoints.py`: `21 passed`

## Cobertura nova adicionada

Servico:

- desbloqueio manual sobre falta com auditoria persistida
- desbloqueio manual sobre excesso com auditoria persistida
- estabilidade apos recalc
- consumo/limpeza do override por novo recebimento
- consumo/limpeza do override por aumento de previsao
- erros de modo interno, quantidade invalida, exceder bloqueio, ausencia de bloqueio

Endpoints:

- `POST /recebimentos` retorna recebimento + inventario
- `GET /inventario` lista snapshots e aplica filtros
- `POST /inventario/desbloqueio-manual` persiste auditoria e override
- `403` para nao-NPBB nas novas escritas
- `404` de configuracao ausente para recebimentos e inventario
- `400` para tipo inativo em recebimentos

## Pontos para auditoria do Opus

1. Validar a semantica do override persistente: ele permanece enquanto houver bloqueio do mesmo tipo e e capado quando o bloqueio natural diminui. Confirmar se isto atende integralmente o requisito de nao "ressuscitar" credito antigo.
2. Confirmar se `disponivel` calculado como `min(recebido_confirmado, planejado) + credito_manual - distribuido` e o comportamento certo para:
   - falta de recebimento
   - excedente da ticketeira
3. Revisar a decisao de alterar a migration existente em vez de criar nova revisao, incluindo `upgrade()` / `downgrade()`.
4. Confirmar se `GET /inventario` sem recalc forcado e aceitavel para v1, dado que ele le apenas o snapshot materializado.
5. Verificar se os codigos HTTP escolhidos no router seguem a convencao mais adequada do repo.
6. Confirmar se `require_npbb_user` satisfaz o papel de "admin" referido no plano/PRD.
7. Revisar se os novos constraints SQL e nomes de indices estao coerentes com o padrao do projeto.

## Riscos / observacoes

- `backend/app/services/inventario_ingressos.py`, `backend/tests/test_inventario_ingressos_service.py` e a migration ainda aparecem como ficheiros nao rastreados no worktree atual; tratar isso no review/commit final conforme a branch em uso.
- Nao executei um ciclo Alembic `upgrade/downgrade` nesta rodada; a validacao feita foi funcional via suites de servico e endpoints.
