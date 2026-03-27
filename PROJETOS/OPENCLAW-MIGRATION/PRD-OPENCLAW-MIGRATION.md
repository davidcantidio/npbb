---
doc_id: "PRD-OPENCLAW-MIGRATION.md"
version: "1.0"
status: "approved"
owner: "PM"
last_updated: "2026-03-25"
project: "OPENCLAW-MIGRATION"
intake_kind: "refactor"
source_mode: "backfilled"
origin_project: "OPENCLAW-MIGRATION"
origin_phase: "nao_aplicavel"
origin_audit_id: "nao_aplicavel"
origin_report_path: "nao_aplicavel"
product_type: "platform-capability"
delivery_surface: "docs-governance"
business_domain: "governanca"
criticality: "alta"
data_sensitivity: "interna"
integrations:
  - "PROJETOS/COMUM"
  - ".codex/skills/openclaw-*"
  - "openclaw-projects.sqlite"
change_type: "migracao"
audit_rigor: "standard"
---

# PRD - OPENCLAW-MIGRATION

## 0. Rastreabilidade

- **Intake de origem**: [INTAKE-OPENCLAW-MIGRATION.md](./INTAKE-OPENCLAW-MIGRATION.md)
- **Modo de origem**: `backfilled`
- **Documento base do backfill**: este PRD consolidado a partir das specs e auditorias do projeto
- **Spec da onda 1**: [openclaw-migration-spec.md](./openclaw-migration-spec.md)
- **Spec derivada de execução end-to-end**: [openclaw-alignment-spec.md](./openclaw-alignment-spec.md)
- **Auditorias materialmente relevantes**:
  - [RELATORIO-AUDITORIA-MIGRATION-R01.md](./auditorias/RELATORIO-AUDITORIA-MIGRATION-R01.md)
  - [RELATORIO-AUDITORIA-MIGRATION-R02.md](./auditorias/RELATORIO-AUDITORIA-MIGRATION-R02.md)

## 1. Resumo Executivo

- **Nome do projeto**: Alinhamento end-to-end do framework OpenClaw ao paradigma `Feature -> User Story -> Task`
- **Tese em 1 frase**: Consolidar governanca, prompts, scaffold, smoke, skills e indice SQLite para que o framework nasca e opere integralmente no modelo canonico.
- **Valor esperado em 3 linhas**:
  - Eliminar divergencia entre superficie documental e bootstrap real do framework.
  - Fazer o indice SQLite v4 reflectir projectos reais criados pelo proprio toolkit.
  - Garantir que execucao, revisao, auditoria e remediacao compartilhem o mesmo contrato operacional.

## 2. Problema ou Oportunidade

- **Problema atual**: o repositório ja migrou parte da governanca e das skills, mas o bootstrap real ainda preserva elementos legados e o fluxo end-to-end nao fecha no formato canonico.
- **Evidência do problema**: scaffolder e smoke ainda mantem superficies antigas; o SQLite estruturado permanece vazio para projectos reais; as auditorias de migracao apontaram drift operacional.
- **Custo de não agir**: o framework continua semanticamente correcto no papel e operacionalmente incoerente na pratica.
- **Por que agora**: existe massa critica de governanca ja migrada; falta consolidar a entrada do sistema, a validacao e a rastreabilidade documental num unico PRD canónico.

## 3. Público e Operadores

- **Usuário principal**: agentes OpenClaw
- **Usuário secundário**: mantenedores do toolkit e do repositório
- **Operador interno**: agente senior de review/auditoria
- **Quem aprova ou patrocina**: PM

## 4. Jobs to be Done

- **Job principal**: operar o framework end-to-end em `Feature -> User Story -> Task`
- **Jobs secundários**:
  - criar projectos novos ja elegiveis para o `boot-prompt.md`
  - validar smoke local/remoto contra o paradigma novo
  - popular o SQLite v4 com dados estruturados reais do projecto
- **Tarefa atual que será substituída**: bootstrap e validacao centrados em `Fase -> Epico -> Issue -> Sprint`

## 5. Escopo

### Dentro

- consolidacao das Features 1-3 da migracao documental original
- alinhamento end-to-end do scaffold, smoke, projecto smoke, indice SQLite v4 e metadata das skills
- validacao canónica de execucao, revisao, auditoria e remediacao
- actualizacao dos testes documentais e de integracao necessarios

### Fora

- migracao mecanica de todos os projectos legados em `PROJETOS/*`
- alteracoes em codigo de aplicacoes de produto fora deste repositorio
- reescrita de historico Git para apagar artefactos legados ja auditados

## 6. Resultado de Negócio e Métricas

- **Objetivo principal**: framework funcional e auditavel no paradigma `Feature -> User Story -> Task`
- **Métricas leading**:
  - novos projectos nao geram `F1-*`, `issues/` nem `SPRINT-*`
  - smoke valida apenas o fluxo canonico
  - referencias legadas activas ficam restritas a compatibilidade explicitamente marcada
- **Métricas lagging**:
  - SQLite v4 populado em `features`, `user_stories`, `tasks` e `feature_audits` para projectos novos
  - veredito `go` nas auditorias de migracao remanescentes
- **Critério mínimo para considerar sucesso**: todas as features abaixo completas, sem bloqueio em scaffold, smoke, review/audit/remediation ou populacao estruturada do indice

## 7. Restrições e Guardrails

- **Restrições técnicas**: Markdown continua fonte de verdade; SQLite continua indice derivado
- **Restrições operacionais**: gate humano apenas em Intake e PRD; gates seniores apos PRD; `GOV-COMMIT-POR-TASK.md` permanece obrigatório
- **Restrições legais ou compliance**: nao_aplicavel
- **Restrições de prazo**: nao_definido
- **Restrições de design ou marca**: nao_aplicavel

## 8. Dependências e Integrações

- **Sistemas internos impactados**: `PROJETOS/COMUM/`, `.codex/skills/openclaw-*`, `scripts/criar_projeto.py`, `bin/check-openclaw-smoke.sh`, `scripts/openclaw_projects_index/`
- **Sistemas externos impactados**: sandbox/gateway usado no smoke remoto
- **Dados de entrada necessários**: specs do projecto, relatórios de auditoria, estado actual do SQLite
- **Dados de saída esperados**: PRD coerente, intake retroativo coerente, artefactos actualizados e validacoes verdes

## 9. Arquitetura Geral do Projeto

- **Backend**: nao_aplicavel
- **Frontend**: nao_aplicavel
- **Banco/migrações**: indice derivado `openclaw-projects.sqlite`
- **Observabilidade**: smoke local/remoto e auditorias documentais
- **Autorização/autenticação**: nao_aplicavel
- **Rollout**: por Feature, User Story e Task, com commits intermediarios e sync do indice apos gravacoes relevantes

## 10. Riscos Globais

- **Risco de produto**: coexistencia prolongada entre superficies legadas e canonicas confundir operadores
- **Risco técnico**: caminhos e wrappers locais permanecerem apontando para artefactos removidos
- **Risco operacional**: smoke verde mascarar scaffold antigo ou SQLite estruturado vazio
- **Risco de dados**: divergencia entre Markdown e indice derivado se o sync nao for executado
- **Risco de adoção**: consumidores ainda dependentes de nomenclatura historica exigirem compatibilidade residual

## 11. Não-Objetivos

- remover todos os documentos legados do repositório nesta rodada
- migrar todos os projectos historicos para `features/.../user-stories/...`
- alterar runtime, credenciais ou infraestrutura fora do toolkit OpenClaw

---

# 12. Features do Projeto

> Decomposicao detalhada da onda documental original: [openclaw-migration-spec.md](./openclaw-migration-spec.md).  
> Decomposicao detalhada da consolidacao end-to-end: [openclaw-alignment-spec.md](./openclaw-alignment-spec.md).

## Feature 1: Documentos de Governanca Centrais

- **depende_de**: []

### Objetivo de Negócio

Definir no master e no scrum do framework a cadeia `Feature > User Story > Task` e os limites de User Story.

### Critérios de Aceite

- [ ] `GOV-FRAMEWORK-MASTER.md` descreve a hierarquia canónica e as fontes de verdade correctas
- [ ] `GOV-SCRUM.md` nao usa Sprint, Epico ou Fase como cadeia operacional principal
- [ ] `GOV-USER-STORY.md` define limites numericos e DoD de User Story

### User Stories planejadas

| US ID | Título | SP estimado | Depende de |
|-------|--------|-------------|------------|
| US-1.1 | Atualizar GOV-FRAMEWORK-MASTER.md | 5 | - |
| US-1.2 | Atualizar GOV-SCRUM.md | 5 | US-1.1 |
| US-1.3 | Criar/alinhar GOV-USER-STORY.md | 3 | - |

## Feature 2: Templates de Artefato

- **depende_de**: ["Feature 1"]

### Objetivo de Negócio

Disponibilizar templates coerentes com PRD feature-centric e User Story canónica.

### Critérios de Aceite

- [ ] `TEMPLATE-USER-STORY.md` existe com frontmatter e campos canonicos
- [ ] `TEMPLATE-PRD.md`, `TEMPLATE-AUDITORIA-FEATURE.md` e `TEMPLATE-ENCERRAMENTO.md` estao alinhados
- [ ] `TEMPLATE-TASK.md` mantem TDD e rastreabilidade

### User Stories planejadas

| US ID | Título | SP estimado | Depende de |
|-------|--------|-------------|------------|
| US-2.1 | Atualizar TEMPLATE-PRD.md | 3 | US-1.1 |
| US-2.2 | Criar TEMPLATE-USER-STORY.md | 3 | US-1.3 |
| US-2.3 | Criar TEMPLATE-AUDITORIA-FEATURE.md | 3 | US-2.1 |
| US-2.4 | Criar TEMPLATE-ENCERRAMENTO.md | 2 | US-2.1 |

## Feature 3: Documentos Operacionais e Skills

- **depende_de**: ["Feature 1", "Feature 2"]

### Objetivo de Negócio

Fazer `boot-prompt.md`, `SESSION-*` e skills operarem no mesmo vocabulário `Feature/US/Task`.

### Critérios de Aceite

- [ ] niveis 4-6 do `boot-prompt.md` operam em `Feature > User Story > Task`
- [ ] `SESSION-IMPLEMENTAR-US.md` e `SESSION-AUDITAR-FEATURE.md` sao os entrypoints corretos
- [ ] `SESSION-MAPA.md` e skills relevantes apontam apenas para a superficie activa

### User Stories planejadas

| US ID | Título | SP estimado | Depende de |
|-------|--------|-------------|------------|
| US-3.1 | Atualizar boot-prompt.md | 5 | US-2.2 |
| US-3.2 | SESSION-IMPLEMENTAR-US.md | 3 | US-3.1 |
| US-3.3 | SESSION-AUDITAR-FEATURE.md | 3 | US-3.1 |
| US-3.4 | Atualizar skills e SESSION-MAPA.md | 3 | US-3.2, US-3.3 |

## Feature 4: Scaffold Canonico de Projeto

- **depende_de**: ["Feature 1", "Feature 2", "Feature 3"]

### Objetivo de Negócio

Fazer novos projectos nascerem directamente no formato `Feature -> User Story -> Task`.

### Critérios de Aceite

- [ ] `scripts/criar_projeto.py` nao gera `F1-*`, `issues/` nem `SPRINT-*`
- [ ] wrappers locais do projecto apontam para `SESSION-IMPLEMENTAR-US`, `SESSION-REVISAR-US` e `SESSION-AUDITAR-FEATURE`
- [ ] `tests/test_criar_projeto.py` valida apenas a arvore canónica

### User Stories planejadas

| US ID | Título | SP estimado | Depende de |
|-------|--------|-------------|------------|
| US-4.1 | Migrar scripts/criar_projeto.py para scaffold canonico | 5 | US-3.4 |
| US-4.2 | Reescrever wrappers locais do bootstrap do projecto | 3 | US-4.1 |
| US-4.3 | Reescrever testes do scaffold para o formato canonico | 3 | US-4.1 |

## Feature 5: Smoke Test e Projeto de Referencia Canonicos

- **depende_de**: ["Feature 4"]

### Objetivo de Negócio

Garantir que o smoke verde prove aderencia ao paradigma novo, e nao apenas ao legado.

### Critérios de Aceite

- [ ] smoke local valida apenas `SESSION-*` e caminhos canonicos
- [ ] smoke remoto falha quando `features`, `user_stories` ou `tasks` nao forem populadas no SQLite v4
- [ ] `PROJETOS/OC-SMOKE-SKILLS/GUIA-TESTE-SKILLS.md` descreve apenas o fluxo canonico

### User Stories planejadas

| US ID | Título | SP estimado | Depende de |
|-------|--------|-------------|------------|
| US-5.1 | Reescrever o smoke test | 5 | US-4.1 |
| US-5.2 | Migrar OC-SMOKE-SKILLS para a arvore canonica | 5 | US-5.1 |

## Feature 6: Fluxo Completo de Execucao, Revisao, Auditoria e Remediacao

- **depende_de**: ["Feature 3", "Feature 4"]

### Objetivo de Negócio

Fechar o ciclo operacional end-to-end no paradigma novo, sem backlog paralelo indevido.

### Critérios de Aceite

- [ ] execucao, review e feature audit usam o mesmo contrato de parametros
- [ ] `REVIEW_MODE` tem precedencia deterministica documentada e testada
- [ ] `same-feature | new-intake | cancelled` ficam estabelecidos como destinos canonicos de remediacao

### User Stories planejadas

| US ID | Título | SP estimado | Depende de |
|-------|--------|-------------|------------|
| US-6.1 | Validar execucao canonica | 3 | US-4.1 |
| US-6.2 | Validar revisao canonica | 3 | US-6.1 |
| US-6.3 | Validar auditoria de feature | 3 | US-6.2 |
| US-6.4 | Validar remediacao pos-hold | 3 | US-6.3 |

## Feature 7: Banco de Dados e Queries Estruturadas Reais

- **depende_de**: ["Feature 4", "Feature 5"]

### Objetivo de Negócio

Fazer o SQLite v4 reflectir projectos reais do framework, nao apenas fixtures.

### Critérios de Aceite

- [ ] um projecto criado pelo scaffold canonico popular `features`, `user_stories`, `tasks` e `feature_audits`
- [ ] projectos legados continuam indexados em `documents` sem poluir o modelo estruturado
- [ ] existe teste de integracao criando projecto, rodando sync e validando SQL minima

### User Stories planejadas

| US ID | Título | SP estimado | Depende de |
|-------|--------|-------------|------------|
| US-7.1 | Validar ingestao estruturada real no indice v4 | 5 | US-5.2 |

## Feature 8: Toolchain de Metadata das Skills

- **depende_de**: ["Feature 3", "Feature 5"]

### Objetivo de Negócio

Eliminar drift entre `SKILL.md`, `agents/openai.yaml` e scripts de deploy.

### Critérios de Aceite

- [ ] `bin/codex-skills-common.sh` emite labels canonicos
- [ ] `agents/openai.yaml` visiveis nao usam `Issue`, `Phase`, `Epic` ou `Sprint` como superficie principal
- [ ] existe cobertura de teste para blindar a metadata das skills

### User Stories planejadas

| US ID | Título | SP estimado | Depende de |
|-------|--------|-------------|------------|
| US-8.1 | Blindar metadata canonica das skills | 3 | US-5.1 |

## 13. Dependências Externas

| Dependência | Tipo | Origem | Impacto | Status |
|-------------|------|--------|---------|--------|
| OpenRouter | API | runtime host | review e auditoria senior | active |
| gateway sandbox | ambiente | smoke remoto | validacao end-to-end | active |

## 14. Rollout e Comunicação

- **Estratégia de rollout**: implementar e validar por Feature, User Story e Task, com smoke e sync do indice nos marcos relevantes
- **Comunicação de mudanças**: `AUDIT-LOG.md`, relatórios em `auditorias/` e documentação canónica em `PROJETOS/COMUM/`
- **Treinamento necessário**: leitura de `SESSION-MAPA.md`, `boot-prompt.md` e documentos de intake/PRD/planning actualizados
- **Suporte pós-launch**: remediacao via `OPENCLAW-MIGRATION` ate estabilizacao completa do paradigma novo

## 15. Revisões e Auditorias

- **Auditorias planejadas**: rodadas de auditoria da migracao ate `go`
- **Critérios de auditoria**: `GOV-AUDITORIA.md` e `SPEC-ANTI-MONOLITO.md` quando aplicavel
- **Critérios de verificacao funcional**: scaffold canónico, smoke canónico, SQLite estruturado, skills e sessions alinhadas

## 16. Checklist de Prontidão

- [x] intake referenciado
- [x] source_mode de backfill declarado
- [x] features definidas com critérios de aceite verificáveis
- [x] dependências entre features declaradas
- [x] riscos e restrições mapeados
- [x] métricas de sucesso declaradas

## 17. Anexos e Referências

- [INTAKE-OPENCLAW-MIGRATION.md](./INTAKE-OPENCLAW-MIGRATION.md)
- [openclaw-migration-spec.md](./openclaw-migration-spec.md)
- [openclaw-alignment-spec.md](./openclaw-alignment-spec.md)
- [AUDIT-LOG.md](./AUDIT-LOG.md)
