---
doc_id: "US-7-02-AUTENTICACAO-INTEGRADOR"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
task_instruction_mode: "required"
feature_id: "FEATURE-7"
decision_refs: []
---

# US-7-02 - Autenticacao do integrador

## User Story

**Como** responsavel por seguranca da plataforma,
**quero** autenticar e isolar identidades de integradores externos (token, mTLS ou padrao ja adotado no monolito),
**para** que apenas clientes autorizados invoquem operacoes de ingestao e para que escopos e segredos fiquem auditaveis.

## Feature de Origem

- **Feature**: FEATURE-7 - Contratos de API para automacao externa (ticketeiras)
- **Comportamento coberto**: criterio de aceite da feature sobre autenticacao definida e testada; alinhamento ao PRD sec. 4.2 e manifesto sec. 6.2 / impacts Backend (segredos, escopos).

## Contexto Tecnico

- Reutilizar padrao existente no backend NPBB quando possivel (API keys, JWT de servico, mTLS terminado no edge, etc.); documentar a escolha na implementacao.
- Rate limiting ou quotas por integrador, se aplicavel, podem iniciar nesta US ou ser estendidos na US-7-03 conforme esforco nas tasks.
- US-7-03 depende desta US para proteger routers de ingestao.

## Plano TDD (opcional no manifesto da US)

- **Red**: nao aplicavel (planejamento; TDD na desdobramento em tasks).
- **Green**: nao aplicavel
- **Refactor**: nao aplicavel

## Criterios de Aceitacao (Given / When / Then)

- **Given** um integrador sem credencial valida,
  **when** chamar qualquer rota de ingestao protegida,
  **then** recebe resposta 401/403 (ou equivalente acordado) sem efeitos colaterais em dados de negocio.
- **Given** um integrador com credencial valida e escopo adequado,
  **when** chamar rotas permitidas (apos US-7-03),
  **then** a identidade do integrador e propagada ao contexto de request (ex.: para logs e idempotencia).
- **Given** a decisao de mecanismo (token, mTLS ou padrao monolito),
  **when** a US for concluida,
  **then** existem testes automatizados que cobrem pelo menos um caminho positivo e um negativo de autenticacao.

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Todas as tasks tem `depends_on`, `parallel_safe` e `write_scope` coerentes com a ordem de execucao
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

| Ordem | ID | Titulo | Estado | Documento |
|-------|----|--------|--------|-----------|
| 1 | T1 | Decisao e contrato do mecanismo de autenticacao do integrador | todo | [TASK-1.md](./TASK-1.md) |
| 2 | T2 | Dependencia FastAPI e respostas 401/403 sem efeitos colaterais | todo | [TASK-2.md](./TASK-2.md) |
| 3 | T3 | Validacao de segredos e escopos por integrador | todo | [TASK-3.md](./TASK-3.md) |
| 4 | T4 | Testes automatizados, rota de verificacao e documentacao operacional minima | todo | [TASK-4.md](./TASK-4.md) |

Execucao: `PROJETOS/COMUM/SESSION-IMPLEMENTAR-TASK.md` ou fila em `SESSION-IMPLEMENTAR-US.md`.

## Arquivos Reais Envolvidos

- `backend/` middleware, dependencias FastAPI, configuracao e testes (caminhos exatos nas tasks)
- [FEATURE-7.md](../../FEATURE-7.md)

## Artefato Minimo

- Integracao de autenticacao aplicavel as rotas de ingestao e evidencia de testes conforme criterios acima.

## Handoff para Revisao Pos-User Story

status: nao_iniciado
base_commit: nao_informado
target_commit: nao_informado
evidencia: nao_informado
commits_execucao: []
validacoes_executadas: []
arquivos_de_codigo_relevantes: []
limitacoes: []

## Dependencias

- [FEATURE-7](../../FEATURE-7.md)
- [FEATURE-2](../../../FEATURE-2-DOMINIO-COEXISTENCIA-E-ROLOUT/FEATURE-2.md)
- [FEATURE-3](../../../FEATURE-3-CATEGORIAS-E-MODOS-FORNECIMENTO/FEATURE-3.md)
- [FEATURE-4](../../../FEATURE-4-RECEBIMENTO-CONCILIACAO-E-BLOQUEIOS/FEATURE-4.md)
- [PRD ATIVOS-INGRESSOS](../../../../PRD-ATIVOS-INGRESSOS.md)
- Outras USs: pode executar em paralelo a US-7-01 se credenciais nao dependerem do schema de idempotencia; caso contrario, depende de US-7-01 `done`
- [GOV-USER-STORY.md](../../../../COMUM/GOV-USER-STORY.md)

## Navegacao Rapida

- [FEATURE-7](../../FEATURE-7.md)
