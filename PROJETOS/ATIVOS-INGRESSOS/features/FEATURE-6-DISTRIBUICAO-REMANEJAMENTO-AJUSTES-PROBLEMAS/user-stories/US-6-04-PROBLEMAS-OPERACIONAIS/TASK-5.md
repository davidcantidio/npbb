---
doc_id: "TASK-5.md"
user_story_id: "US-6-04-PROBLEMAS-OPERACIONAIS"
task_id: "T5"
version: "2.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T2"
parallel_safe: false
write_scope:
  - "PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-8-DASHBOARD-ATIVOS-OPERACIONAL/FEATURE-8.md"
  - "backend/app/routers/ingressos.py"
  - "backend/app/main.py"
tdd_aplicavel: false
---

# T5 - Handoff FEATURE-8: contrato de leitura e observabilidade

## objetivo

Documentar para a **FEATURE-8** (dashboard / painel de ocorrencias) o **contrato de leitura** estavel: metodo HTTP, path, query params de filtro/paginacao, forma do JSON e lista de campos que o painel pode consumir **sem duplicar regras de negocio**. Alinhar **observabilidade**: propagar ou registar `correlation_id` nos handlers da API de problemas quando o projeto tiver middleware ou header padronizado.

## precondicoes

- T2 `done`: endpoints e schemas estaveis (ajustes cosméticos apenas com sync desta documentacao).
- Manifesto ou pasta da FEATURE-8 disponivel para referencia cruzada (criar subsecao ou ficheiro de handoff apenas se o fluxo do projeto permitir editar FEATURE-8 nesta fase; caso contrario, registrar o contrato no proprio comentario/README da US ou em `SCOPE-LEARN.md` conforme [GOV-USER-STORY.md](../../../../../COMUM/GOV-USER-STORY.md)).

## orquestracao

- `depends_on`: `T2` (contrato API existe).
- `parallel_safe`: false (pode sobrepor documentacao da FEATURE-8 se no `write_scope`).

## arquivos_a_ler_ou_tocar

- Endpoints implementados na T2 (codigo fonte)
- `backend/app/main.py` *(middleware global, se houver)*
- Pasta `PROJETOS/ATIVOS-INGRESSOS/features/` — localizar `FEATURE-8*` para linkar contrato
- [FEATURE-6.md](../../FEATURE-6.md) *(observabilidade / trilha)*

## passos_atomicos

1. Extrair do OpenAPI gerado (ou do codigo) a especificacao exata: paths, codigos de resposta, schema de item e de listagem.
2. Redigir tabela **Campo | Tipo | Obrigatorio | Uso no painel** para consumo pela FEATURE-8; colar no README da FEATURE-8 ou anexo acordado pelo PM.
3. Verificar se FastAPI/request ja expoe `X-Request-ID` / `correlation_id`; se sim, incluir leitura opcional no POST e persistir na coluna da T1 quando existir; se nao, adicionar logging estruturado com `correlation_id` gerado por request no handler (sem alterar semantica de negocio). Referencia cruzada: [US-8-04](../../../FEATURE-8-DASHBOARD-ATIVOS-OPERACIONAL/user-stories/US-8-04-SERIE-TEMPORAL-OCORRENCIAS-E-METRICAS-PRD/README.md) (serie temporal / ocorrencias) quando documentar o contrato.
4. Garantir que logs de erro nestes endpoints nao vazam PII (seguir `log_sanitize` se aplicavel no repo).

## comandos_permitidos

- `cd backend && PYTHONPATH=<raiz>:<raiz>/backend .venv/bin/python -c "from app.main import app; print(app.openapi())"` *(inspecao rapida do schema; opcional)*
- `cd backend && ruff check app/routers/ingressos.py`

## resultado_esperado

FEATURE-8 tem documentacao suficiente para implementar agregacoes/drill-down sem reabrir o modelo desta US; endpoints registram trilha minimamente rastreavel.

## testes_ou_validacoes_obrigatorias

- Revisao manual: documento de handoff referenciado a partir do README da FEATURE-8 ou da US.
- Se `correlation_id` for persistido: um teste em T3 ou extensao leve confirmando presenca opcional (pode ser task de follow-up se escopo apertar).

## stop_conditions

- Parar se FEATURE-8 ainda nao existir no repositorio — manter contrato apenas no README desta US ate a feature ser criada.
- Parar se observabilidade exigir middleware global inexistente — documentar lacuna e abrir follow-up para fundacao transversal.
