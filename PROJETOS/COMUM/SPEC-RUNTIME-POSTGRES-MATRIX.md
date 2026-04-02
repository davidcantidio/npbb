---
doc_id: "SPEC-RUNTIME-POSTGRES-MATRIX.md"
version: "1.2"
status: "active"
owner: "PM"
last_updated: "2026-03-30"
---

# SPEC — Matriz runtime: quando o Postgres (read model) e obrigatorio

Este documento reduz exploracao ad-hoc por agentes: define **quando** tentar sync,
**o que fazer** quando a URL nao existe e **qual ordem** de comandos usar.
Contrato detalhado do indice: `SPEC-INDICE-PROJETOS-POSTGRES.md`.
Comportamento do pipeline de sync: `scripts/fabrica_projects_index/README.md`.

## 1. Variaveis e ficheiros (referencia rapida)

| Nome | Papel |
|------|--------|
| `FABRICA_PROJECTS_DATABASE_URL` | URL Postgres do read model; obrigatoria para sync real |
| `FABRICA_REPO_ROOT` | Raiz do clone (contem `PROJETOS/`); o wrapper em `bin/` preenche quando ausente |
| `FABRICA_PGSSLMODE` | Opcional; anexado a URL se nao houver `sslmode=` |
| `~/.config/nemoclaw-host/host.env` | Fonte canonica local (fora do Git) carregada por `bin/fabrica-projects-db-host-env.sh` |
| `config/host.env.example` | Exemplo versionado; **nao** contem segredos |

**Ordem operacional tipica** (primeira vez ou novo host):

1. Copiar/definir `host.env` no caminho acima com `FABRICA_PROJECTS_DATABASE_URL` (e SSL se preciso).
2. Rode `./bin/ensure-fabrica-projects-index-runtime.sh` como preflight canonico barato.
3. Se o schema ainda nao existir: `./bin/bootstrap-fabrica-projects-postgres.sh` (flags conforme necessidade; ex. `--skip-chunks` para so schema + sync sem embeddings).
4. `./bin/sync-fabrica-projects-db.sh` a partir da raiz do repo OpenClaw.

**Nada disto entra em commit:** credenciais e `host.env` do utilizador permanecem fora do Git.

## 2. Matriz: sync obrigatorio vs opcional

| Contexto | Preflight / sync antes de agir? | Se a URL estiver ausente |
|----------|------------------------------|---------------------------|
| `SESSION-IMPLEMENTAR-US` | `ensure-...` sempre; `sync` quando o preflight passar | se a task ou validacao depender explicitamente de Postgres/sync real, `BLOQUEADO`; se o fluxo for apenas documental, registar `DRIFT_INDICE` e seguir com Markdown + Git |
| `SESSION-REVISAR-US` | `ensure-...` sempre; `sync` quando o preflight passar | mesma regra: runtime real bloqueia cedo; revisao puramente documental pode continuar com `DRIFT_INDICE` |
| `SESSION-AUDITAR-FEATURE` | `ensure-...` sempre; `sync` quando o preflight passar | auditoria documental continua com `DRIFT_INDICE`; checks que dependam de `sync_runs` ou DB real ficam assinalados como nao verificaveis |
| `SESSION-DECOMPOR-*` (PRD/Feature/US/Tasks) | `ensure-... --allow-missing-url` recomendado; `sync` so se o preflight passar | registar `DRIFT_INDICE`; a etapa continua em Markdown + Git |
| `SESSION-REMEDIAR-HOLD` | `ensure-... --allow-missing-url` recomendado; `sync` se passar | registar `DRIFT_INDICE`; continuar documentalmente |
| `SESSION-PLANEJAR-PROJETO` | `ensure-... --allow-missing-url` recomendado; `sync` se passar | registar `DRIFT_INDICE`; continuar documentalmente |
| Tasks **so documentais** (sem validacao contra DB) | `ensure-... --allow-missing-url` opcional; `sync` dispensavel | `DRIFT_INDICE` e Markdown prevalece |
| CI / automacao com secret `FABRICA_PROJECTS_DATABASE_URL` | Obrigatorio quando o job depender do indice | Falha do job e tratada pelo pipeline |

## 3. Regra anti-exploracao (agentes)

Se `./bin/ensure-fabrica-projects-index-runtime.sh` ou
`./bin/sync-fabrica-projects-db.sh` falharem por URL ausente, URL invalida ou
conectividade recusada:

- Registe uma linha em `DRIFT_INDICE` (ou tabela equivalente na sessao).
- Preserve o exit code observavel do preflight (`12`, `13`, `14`, `15` conforme o caso) quando o chamador depender de runtime real.
- **Nao** instale Postgres, Docker, winget, binarios EDB nem crie servicos no host
  como parte da sessao de framework, salvo **pedido explicito humano** nesse sentido.
- A fonte de verdade para estado de governanca continua a ser **Markdown + Git**;
  o indice derivado fica por sincronizar ate o operador configurar o runtime.

## 4. Duas pistas de leitura

- **Pista A (sempre valida):** ler e editar `PROJETOS/**/*.md` conforme GOV.
- **Pista B (quando sync correu):** consultar Postgres para telemetria/agregados;
  em **conflito** com Markdown, **Markdown prevalece** — corrigir Markdown e
  reexecutar sync, nao editar o banco como fluxo canonico de dominio.

## 5. Contrato de implementacao (sync)

Nao re-inferir comportamento do pipeline a partir de sessoes: a descricao
canonica atual do entrypoint, preflight, determinismo e precedencia do Markdown
esta em `scripts/fabrica_projects_index/README.md`, no wrapper
`bin/ensure-fabrica-projects-index-runtime.sh` e em
`bin/sync-openclaw-projects-db.sh`.

## 6. Documentos relacionados

| Documento | Relacao |
|-----------|---------|
| `PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md` | Secao 3 (fontes de verdade); indexa esta matriz |
| `PROJETOS/COMUM/SPEC-INDICE-PROJETOS-POSTGRES.md` | Contrato do read model; aponta para esta matriz |
| `PROJETOS/COMUM/SESSION-MAPA.md` | Entrada interativa; resume matriz e `RUNTIME-WINDOWS.md` |
| `PROJETOS/COMUM/boot-prompt.md` | Leitura obrigatoria nivel 2 (agente autonomo) |
| `SESSION-IMPLEMENTAR-US.md`, `SESSION-REVISAR-US.md`, `SESSION-AUDITAR-FEATURE.md`, `SESSION-DECOMPOR-*.md`, `SESSION-REMEDIAR-HOLD.md`, `SESSION-PLANEJAR-PROJETO.md` | Pre-condicao de sync; bloco normativo que cita esta matriz |
| `AGENTS.md` (raiz do repo OpenClaw) | Postgres e pytest; complementar a `RUNTIME-WINDOWS.md` no Windows |
