# Handoff — Task 2: API de configuração e previsões (Ingressos v2)

Documento para outro modelo **revisar, auditar ou corrigir** a implementação da Task 2 do [`plan.md`](plan.md).

## Objetivo do escopo

API REST sob prefixo **`/ingressos/v2`** para:

1. Configurar tipos de ingresso ativos e modo de fornecimento por evento.
2. Auditar mudanças de modo de fornecimento.
3. Criar/atualizar previsões por `(diretoria, tipo_ingresso)`.
4. Listar previsões com filtros.

**Fora de escopo:** reconciliação, inventário materializado, distribuição, PDF, integrações OpenClaw (Task 3+).

## Ficheiros principais (ordem sugerida de leitura)

1. [`backend/app/routers/ingressos_v2.py`](backend/app/routers/ingressos_v2.py) — rotas e regras de negócio.
2. [`backend/app/schemas/ingressos_v2.py`](backend/app/schemas/ingressos_v2.py) — contratos Pydantic.
3. [`backend/app/models/ingressos_v2_models.py`](backend/app/models/ingressos_v2_models.py) — `ConfiguracaoIngressoEvento`, `ConfiguracaoIngressoEventoTipo`, `PrevisaoIngresso`, `AuditoriaIngressoEvento`.
4. [`backend/app/routers/eventos/_shared.py`](backend/app/routers/eventos/_shared.py) — `_check_evento_visible_or_404` (visibilidade por agência).
5. [`backend/app/platform/security/rbac.py`](backend/app/platform/security/rbac.py) — `require_npbb_user` (escrita “admin interno”).
6. [`backend/app/main.py`](backend/app/main.py) — `include_router(ingressos_v2_router)`.
7. [`backend/tests/test_ingressos_v2_endpoints.py`](backend/tests/test_ingressos_v2_endpoints.py) — testes de regressão.

## Contrato HTTP (resumo)

| Método | Caminho | Auth | Comportamento esperado |
|--------|---------|------|-------------------------|
| `POST` | `/ingressos/v2/eventos/{evento_id}/configuracao` | `require_npbb_user` | Cria config + tipos; `409` se já existir; visibilidade do evento. |
| `GET` | `/ingressos/v2/eventos/{evento_id}/configuracao` | `get_current_user` | Lê config + tipos; `404` se config inexistente (`CONFIGURACAO_INGRESSO_NOT_FOUND`). |
| `PATCH` | `/ingressos/v2/eventos/{evento_id}/configuracao` | `require_npbb_user` | Body deve ter pelo menos um campo útil; atualiza modo e/ou tipos; **se modo mudar**, append em `AuditoriaIngressoEvento` com `usuario_id`. |
| `POST` | `/ingressos/v2/eventos/{evento_id}/previsoes` | `require_npbb_user` | Exige config; valida diretoria; tipo deve estar ativo na config; **upsert** por tripleta. |
| `GET` | `/ingressos/v2/eventos/{evento_id}/previsoes` | `get_current_user` | Exige config; filtros query opcionais `diretoria_id`, `tipo_ingresso`. |

Enums relevantes: `ModoFornecimento`, `TipoIngresso` em `app.models.models`.

## Regras de negócio importantes

- **Um config por evento:** `UniqueConstraint("evento_id")` em `ConfiguracaoIngressoEvento`; API devolve `409 CONFIGURACAO_INGRESSO_DUPLICATE` em corrida ou duplicata explícita.
- **Tipos ativos:** só tipos listados em `ConfiguracaoIngressoEventoTipo` são válidos para `POST .../previsoes` (`TIPO_INGRESSO_INVALID_FOR_EVENT`).
- **Substituição de tipos no PATCH:** `_replace_config_tipos` faz delete + insert dos tipos. Ao remover um tipo ativo, podem existir `PrevisaoIngresso` para esse tipo — o revisor deve confirmar se o produto exige limpeza, bloqueio ou apenas documentação.
- **Auditoria:** só quando `modo_fornecimento` no payload **diferir** do valor atual; mudança só de tipos **não** gera auditoria (ver teste `test_patch_configuracao_tipos_sem_auditoria`).
- **“Admin role” no plano:** implementação usa **`UsuarioTipo.NPBB`** via `require_npbb_user`, não uma role `admin` separada. Auditar se isso cumpre o PRD para o ambiente alvo.

## Visibilidade

Todos os endpoints relevantes chamam `_check_evento_visible_or_404`: utilizadores **agência** só veem eventos da própria `agencia_id`; para evento de outra agência costuma devolver `404 EVENTO_NOT_FOUND` (padrão de ocultação).

## Mapa de testes

- Criar + ler config; duplicata `POST` → `409`.
- `GET` config sem linha → `404 CONFIGURACAO_INGRESSO_NOT_FOUND`.
- `PATCH` só tipos → sem linhas em `AuditoriaIngressoEvento`.
- `PATCH` mudança de modo → 1 auditoria, `usuario_id` preenchido.
- `PATCH` `{}` → `400 VALIDATION_ERROR_NO_FIELDS`.
- Previsões: create, upsert, lista, filtro `diretoria_id`; tipo inativo; diretoria inexistente; sem config.
- RBAC: `agencia`/`bb` → `403` em escritas; leitura agência só evento da própria agência.

Comando típico (ajustar `PYTHONPATH` ao SO; ver [`AGENTS.md`](AGENTS.md) / [`docs/SETUP.md`](docs/SETUP.md)):

```bash
cd backend
set TESTING=true
set SECRET_KEY=ci-secret-key
python -m pytest tests/test_ingressos_v2_endpoints.py -q
```

## Checklist de auditoria

1. **Correção:** `PATCH` com mesmo modo que o atual — confirmar que **não** cria linha de auditoria (comportamento desejado).
2. **Segurança:** confirmar que nenhum endpoint expõe config/previsões sem autenticação onde apropriado.
3. **Consistência de dados:** impacto de remover tipo ativo no `PATCH` sobre `PrevisaoIngresso` existentes.
4. **Transações:** fluxo `PATCH` (auditoria + update + commit) — avaliar necessidade de padrão mais explícito em caso de extensão futura.
5. **Alinhamento com `plan.md`:** RBAC “admin” vs NPBB; filtros GET previsões suficientes para o frontend v1.
6. **OpenAPI:** rever Swagger para query params e enums serializados como strings.

## Lacunas opcionais (não bloqueantes da Task 2)

- Teste dedicado: `PATCH` modo **igual** ao atual → zero auditorias.
- Bulk `POST` previsões (lista) — não pedido no plano; hoje é um item por pedido.

## Instrução para o modelo revisor

Ler os ficheiros listados, confirmar invariantes e matriz RBAC, corrigir bugs ou acrescentar testes onde a checklist falhar, manter o diff **mínimo** e alinhado com padrões existentes (`raise_http_error`, dependências FastAPI, SQLModel).
