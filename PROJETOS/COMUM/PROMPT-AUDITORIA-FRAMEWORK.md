---
doc_id: "PROMPT-AUDITORIA-FRAMEWORK.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-26"
---

# Prompt Canonico - Auditoria do Framework / Repositorio

## Como usar

Cole este prompt em uma sessao com acesso ao repositorio quando quiser auditar
o estado atual da Fabrica como framework e runtime operacional.

- este prompt e para auditoria do repositorio inteiro; nao substitui a
  auditoria de feature em `PROJETOS/COMUM/PROMPT-AUDITORIA.md`
- audite a worktree atual ou um commit/base explicito, quando isso fizer parte
  do contexto

## Prompt

Voce e um auditor tecnico senior. Faca uma auditoria completa do repositorio
para verificar se a implementacao atual do framework Fabrica (alias legado:
OpenClaw) v3.0 esta coerente, consistente e operacionalmente correta.

### Objetivo da auditoria

Validar se o framework convergiu, na superficie ativa e operacional, para:

`Intake -> Clarificacao -> PRD -> Features -> User Stories -> Tasks -> Execucao -> Review -> Auditoria de Feature`

com Postgres como unico backend operacional do indice derivado.

### Escopo da auditoria

1. documentos normativos em `PROJETOS/COMUM/`
2. `AGENTS.md`, `PROJETOS/COMUM/boot-prompt.md`, `PROJETOS/COMUM/SESSION-MAPA.md`
3. templates e sessoes de Clarificacao / PRD / Feature / User Story / Task / auditoria
4. skills em `.codex/skills/`
5. scripts e runtime do indice em `scripts/openclaw_projects_index/` e `bin/`
6. `config/host.env.example`, `README.md`
7. testes afetados em `tests/`

### Regras de interpretacao obrigatorias

1. Em `PROJETOS/COMUM/`, considere como canonico principal apenas o que estiver
   com `status: "active"`.
2. Para `AGENTS.md`, `README.md`, `config/host.env.example`, `boot-prompt.md`,
   `SESSION-MAPA.md`, scripts em `bin/` e codigo em `scripts/`, trate-os como
   superficie operacional a validar contra o contrato ativo, mesmo quando nao
   tiverem o mesmo frontmatter normativo.
3. Trate `legacy_reference` e `historical` como legado arquivado; o diretorio
   `PROJETOS/COMUM/LEGADO/` nao faz mais parte do clone lean.
4. Trate `legacy_router` como aceitavel apenas se funcionar como roteador de
   compatibilidade e nao como fluxo operacional concorrente.
5. Nao marque como finding o mero fato de existir legado arquivado, stub de
   compatibilidade ou utilitario explicito de migracao historica.
6. Diferencie explicitamente:
   - compatibilidade historica aceitavel
   - contaminacao indevida do contrato ativo
   - residuo interno/privado que nao vaza para a operacao principal
   - regressao operacional real
7. Para o indice, julgue primeiro a superficie operacional publica: CLI
   principal, variaveis de ambiente, scripts de sync/deploy/smoke, docs
   operacionais, skills e testes.
8. Referencias a SQLite, `issue-local`, `fase`, `issue-first`, `sync_meta` ou
   `SESSION-PLANEJAR-PROJETO` so sao problematicas se reaparecerem como
   contrato ativo, fluxo principal, prova operacional ou requisito para uso
   normal.

### O que verificar obrigatoriamente

1. Se o pipeline ativo inclui `Clarificacao` de forma explicita.
2. Se `Issue/Phase/Epic/Sprint` deixaram de ser modelo operacional vigente e
   aparecem apenas como historico/compatibilidade quando existirem.
3. Se o PRD exige e respeita:
   - `Especificacao Funcional`
   - `Plano Tecnico`
   - `Hipoteses Congeladas`
   - regra de precedencia: em conflito, `Especificacao Funcional` vence
4. Se existe sessao explicita de clarificacao pre-PRD e se ela bloqueia PRD
   ambiguo.
5. Se `TASK-*.md` exige:
   - `depends_on: []`
   - `parallel_safe: false`
   - `write_scope: []`
   e se sessoes/prompts de decomposicao, execucao e review respeitam isso.
6. Se `SESSION-PLANEJAR-PROJETO.md`, quando existir, esta restrito a
   `legacy_router` e encaminha para `SESSION-DECOMPOR-*` em vez de competir com
   a cadeia ativa.
7. Se o runtime operacional do indice e realmente Postgres:
   - `FABRICA_PROJECTS_DATABASE_URL` tratado como variavel operacional
   - ausencia de dependencia operacional de `OPENCLAW_PROJECTS_DB`
   - ausencia de dependencia operacional de `OPENCLAW_PROJECTS_INDEX_BACKEND`
   - smokes/deploys/validacoes usando `sync_runs`, nao `sync_meta`
   - SQLite, se existir, restrito a importacao/migracao historica explicita
8. Se skills, docs e scripts estao convergentes entre si e nao se contradizem.
9. Se os testes cobrem as mudancas principais de v3.0 e se ha lacunas
   relevantes de cobertura.
10. Se ha drift normativo entre documentos ativos.
11. Se ha regressoes praticas ou quebras provaveis em sync, smoke, deploy,
    validacao de host ou runtime do indice.

### Instrucoes de auditoria

- nao altere arquivos
- nao proponha reescrita ampla sem antes apontar o problema concreto
- priorize bugs, contradicoes, regressoes operacionais e lacunas de teste
- use referencias de arquivo e linha sempre que possivel
- ao encontrar legado, classifique como:
  - `compatibilidade aceitavel`
  - `contaminacao do contrato ativo`
  - `residuo interno sem impacto operacional imediato`
- ao avaliar `sync.py` e afins, diferencie interface publica operacional de
  helpers internos ou scripts legados de migracao

### Formato obrigatorio da resposta

1. `Findings`
   - liste primeiro os achados, ordenados por severidade
   - cada achado deve incluir:
     - severidade: `critical`, `high`, `medium` ou `low`
     - classificacao: `contrato ativo`, `operacional`, `teste`,
       `compatibilidade`, `residuo interno`
     - arquivo
     - linha(s) quando possivel
     - explicacao objetiva do risco
     - por que isso viola ou enfraquece o v3.0
2. `Open Questions`
   - apenas duvidas reais que impecam concluir algo
3. `Verdict`
   - `OK`
   - `OK COM RESSALVAS`
   - `NAO OK`
4. `Checklist de conformidade v3.0`
   - marque item por item como `ok`, `parcial` ou `falho`

### Regra final

- Se nao houver findings materiais, diga explicitamente que nao encontrou
  achados materiais.
- Nesse caso, liste apenas riscos residuais, residuos internos sem impacto
  imediato ou gaps de teste.
- Nao trate compatibilidade historica arquivada, `legacy_router` correto ou
  utilitario explicito de migracao SQLite como falha por si so.
