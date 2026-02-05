# Plano de Sprints - Auditoria Eventos

## Atualizacoes desta revisao
- Plano reordenado para refletir backlog detalhado (P1/P2/P3) e dependencias.
- Nenhum item P0 identificado no backlog atual.
- Itens P2 foram distribuídos em sprints separados para caber em capacidade de 1 dev/semana.
- Adicionada matriz de rastreabilidade item -> sprint (todos os itens aparecem exatamente 1 vez).

## Premissas
- Cadencia: sprint de 1 semana.
- Capacidade: 1 dev (5 dias uteis).
- Prioridade: P1 > P2 > P3, e dentro disso menor esforco remove risco primeiro.
- Dependencias externas (registrar como bloqueio quando necessario):
  - Decisao de produto/seguranca: matriz de permissao (NPBB/BB/Agencia) + 404 vs 403.
  - Ops/DBA: janela para criacao de indices (possivel uso de CONCURRENTLY).
  - Deploy: caminho/empacotamento do arquivo de config de data health.

---

## Sprint 1 (P1 - Acesso e risco imediato)
**Objetivo:** fechar risco de exposicao e tornar import menos vulneravel a DoS de memoria.

### Itens
- [P1] Visibilidade de eventos por matriz de permissoes (NPBB / BB / Agencia)
  - Objetivo: aplicar regra de visibilidade uniforme em listagem e detalhe.
  - Esforco: M
  - Dependencias/bloqueios: decisao 404 vs 403; criterio de “NPBB” no modelo.
  - Criterios de aceite:
    - Matriz documentada
    - Testes por perfil (NPBB/BB/Agencia) em list + detail
    - Acesso fora do escopo retorna 404 (ou 403 se definido)
  - Testes/observabilidade: testes de auth/visibilidade por perfil.

- [P1] Importacao CSV de eventos carrega o arquivo inteiro em memoria
  - Objetivo: streaming + limite de tamanho/linhas.
  - Esforco: M
  - Dependencias/bloqueios: definir MAX_CSV_BYTES/MAX_ROWS.
  - Criterios de aceite:
    - Sem uso de `read()`/`list(csv.reader(...))`
    - Rejeita arquivo acima do limite
    - Testes para limite e arquivo valido
  - Testes/observabilidade: testes de upload com limite e erros por linha.

**DoD Sprint 1**
- Testes de eventos/visibilidade/CSV passando
- Logs de import sem PII (mantidos)
- Docs atualizadas se o contrato mudar (limites de import)

---

## Sprint 2 (P1 performance + P2 confiabilidade curta)
**Objetivo:** reduzir risco de performance no listing/export e tornar criacao de evento previsivel em ambientes novos.

### Itens
- [P1] Filtros criticos de eventos sem indices dedicados
  - Objetivo: criar indices nas colunas de filtros (diretoria/status/tipo/subtipo/datas).
  - Esforco: M
  - Dependencias/bloqueios: janela de migracao; decidir indices compostos vs simples.
  - Criterios de aceite:
    - Migracao aplica indices
    - EXPLAIN sem Seq Scan nas queries principais
  - Testes/observabilidade: migracao valida (upgrade/downgrade) e smoke tests.

- [P2] Inferencia de status usa nomes hard-coded; erro 500 se status nao estiver seedado
  - Objetivo: erro controlado (400/409) + instrucao de seed; opcional check no startup.
  - Esforco: P
  - Dependencias/bloqueios: definir comando de seed oficial.
  - Criterios de aceite:
    - Criacao sem status seedado retorna erro amigavel
    - Doc de setup menciona seed obrigatorio
  - Testes/observabilidade: teste de criacao sem seed.

- [P2] Config de saude de dados do evento vive em docs/ com fallback silencioso
  - Objetivo: mover config para runtime + warning quando fallback.
  - Esforco: P/M
  - Dependencias/bloqueios: caminho oficial e inclusao no deploy.
  - Criterios de aceite:
    - Config carregada do path oficial
    - Warning quando fallback
    - Override via env (se definido)
  - Testes/observabilidade: teste de carregamento config.

**DoD Sprint 2**
- Migracoes aplicadas com rollback
- Testes de eventos passam
- Documentacao de seed/config atualizada

---

## Sprint 3 (P2 performance + P3 limpeza)
**Objetivo:** reduzir custo do matching no import e eliminar duplicacao de regra de visibilidade.

### Itens
- [P2] Matching de eventos no import CSV faz scoring em Python por linha
  - Objetivo: mover ranking para SQL ou limitar candidatos com query eficiente.
  - Esforco: M
  - Dependencias/bloqueios: DB (Postgres vs SQLite); regra de overlap precisa permanecer equivalente.
  - Criterios de aceite:
    - Query retorna 1 candidato (LIMIT 1)
    - Testes de equivalencia com regra atual
  - Testes/observabilidade: testes de matching e import.

- [P3] Regras de visibilidade duplicadas em routers relacionados
  - Objetivo: helper unico (ativacao/gamificacao/eventos).
  - Esforco: P
  - Dependencias/bloqueios: depende da matriz definida no Sprint 1.
  - Criterios de aceite:
    - Helper unico usado por routers
    - Tests continuam verdes
  - Testes/observabilidade: smoke tests de endpoints.

**DoD Sprint 3**
- Testes passando
- Sem regressao no import

---

## Sprint 4 (P2 - Refactor estrutural)
**Objetivo:** quebrar router monolitico em submodulos e preparar base para evolucao.

### Itens
- [P2] Router de eventos muito grande e com multiplas responsabilidades
  - Objetivo: separar CRUD/import/export/dicionarios/forms/questionario/gamificacao/ativacao.
  - Esforco: G
  - Dependencias/bloqueios: precisa de testes de smoke antes de iniciar.
  - Criterios de aceite:
    - Paths/contratos mantidos
    - Arquivo principal reduzido (apenas includes)
    - Documentacao de endpoints atualizada
  - Testes/observabilidade: smoke tests para cada subrouter.

**DoD Sprint 4**
- Todos endpoints continuam funcionando
- Documentacao atualizada

---

## Matriz item -> sprint
- [P1] Visibilidade de eventos por matriz de permissoes (NPBB / BB / Agencia) -> Sprint 1
- [P1] Importacao CSV de eventos carrega o arquivo inteiro em memoria -> Sprint 1
- [P1] Filtros criticos de eventos sem indices dedicados -> Sprint 2
- [P2] Inferencia de status usa nomes hard-coded; erro 500 se status nao estiver seedado -> Sprint 2
- [P2] Config de saude de dados do evento vive em `docs/` com fallback silencioso -> Sprint 2
- [P2] Matching de eventos no import CSV faz scoring em Python por linha -> Sprint 3
- [P3] Regras de visibilidade duplicadas em routers relacionados -> Sprint 3
- [P2] Router de eventos muito grande e com multiplas responsabilidades -> Sprint 4
