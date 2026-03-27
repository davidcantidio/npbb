---
doc_id: "INTAKE-OPENCLAW-MIGRATION.md"
version: "1.1"
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

# INTAKE - OPENCLAW-MIGRATION

> Backfill retroativo consolidado a partir de
> [PRD-OPENCLAW-MIGRATION.md](./PRD-OPENCLAW-MIGRATION.md),
> [openclaw-migration-spec.md](./openclaw-migration-spec.md) e
> [openclaw-alignment-spec.md](./openclaw-alignment-spec.md).

## 0. Rastreabilidade de Origem

- projeto de origem: OPENCLAW-MIGRATION
- fase de origem: nao_aplicavel (iniciativa transversal a `PROJETOS/COMUM/`)
- auditoria de origem: nao_aplicavel como origem unica; usar R01/R02 como evidencia complementar
- relatorio de origem: nao_aplicavel
- motivo da abertura deste intake: reconstruir o gate `Intake -> PRD` de forma auditavel a partir do PRD canónico remanescente do projecto

## 1. Resumo Executivo

- nome curto da iniciativa: Alinhamento end-to-end do OpenClaw
- tese em 1 frase: consolidar governanca, scaffold, smoke, skills e indice SQLite para que o framework opere integralmente em `Feature -> User Story -> Task`.
- valor esperado em 3 linhas:
  - Projectos novos nascem directamente em `features/.../user-stories/...`.
  - Smoke local/remoto valida o paradigma novo, em vez de tolerar o legado.
  - O SQLite v4 passa a refletir projectos reais criados pelo proprio framework.

## 2. Problema ou Oportunidade

- problema atual: a governanca e parte das skills ja migraram, mas o bootstrap real do framework ainda preserva superficies legadas e o fluxo end-to-end nao fecha no formato canónico.
- evidencia do problema: PRD consolidado do projecto, specs vigentes e relatórios `MIGRATION-R01` e `MIGRATION-R02`.
- custo de nao agir: o framework continua correcto no papel e incoerente na pratica, com smoke e scaffold podendo validar estruturas antigas.
- por que agora: o projecto ja possui PRD consolidado e escopo claro; falta apenas recompor o gate de intake de forma coerente com esse estado.

## 3. Publico e Operadores

- usuario principal: agentes OpenClaw
- usuario secundario: PM e mantenedores do repositorio toolkit
- operador interno: agente senior (auditoria/revisao)
- quem aprova ou patrocina: PM

## 4. Jobs to be Done

- job principal: operar o framework end-to-end em `Feature -> User Story -> Task`
- jobs secundarios: criar projectos novos canónicos; validar smoke e SQLite estruturado; rever e auditar no mesmo contrato operacional
- tarefa atual que sera substituida: bootstrap e validacao centrados em `Fase > Epico > Issue > Sprint`

## 5. Fluxo Principal Desejado

1. Intake/PRD aprovados (gate humano)
2. Decomposicao em Features e User Stories no PRD
3. Scaffold e smoke operam sobre a mesma arvore canónica do projecto
4. Execucao por User Story ate `ready_for_review`, seguida de revisao senior
5. Auditoria por Feature ate veredito `go`, com remediacao ou encerramento quando aplicavel

## 6. Escopo Inicial

### Dentro

- Actualizacao de `GOV-*`, `TEMPLATE-*`, `SESSION-*`, `boot-prompt.md` e skills listadas no spec
- Depreciacao de prompts legados com ponteiro para substitutos
- Alinhamento do scaffold, smoke, projecto smoke, SQLite v4 e metadata visivel das skills

### Fora

- Codigo de aplicacoes de produto fora deste repositorio
- Migracao mecanica de todos os projectos legados do repositorio numa unica rodada

## 7. Resultado de Negocio e Metricas

- objetivo principal: framework funcional e auditavel no paradigma `Feature -> User Story -> Task`
- metricas leading: scaffold novo sem `F1-*`/`issues/`; smoke validando apenas caminhos canonicos; legados restritos a compatibilidade marcada
- metricas lagging: SQLite v4 populado com `features`, `user_stories`, `tasks` e `feature_audits`; veredito `go` nas auditorias remanescentes
- criterio minimo para considerar sucesso: scaffold, smoke, review/audit/remediation e indice estruturado operando sem dependencia do paradigma antigo

## 8. Restricoes e Guardrails

- restricoes tecnicas: Markdown como fonte de verdade; SQLite derivado
- restricoes operacionais: Gate humano apenas Intake/PRD; gate senior apos PRD
- restricoes legais ou compliance: nao_aplicavel
- restricoes de prazo: nao_definido
- restricoes de design ou marca: nao_aplicavel

## 9. Dependencias e Integracoes

- sistemas internos impactados: `PROJETOS/COMUM/`, `.codex/skills/openclaw-*`, `scripts/criar_projeto.py`, `bin/check-openclaw-smoke.sh`, `scripts/openclaw_projects_index/`
- sistemas externos impactados: sandbox/gateway usado no smoke remoto
- dados de entrada necessarios: PRD consolidado, specs do projecto, relatórios de auditoria e estado actual do SQLite
- dados de saida esperados: artefactos actualizados, smoke canónico verde e audit log coerente

## 10. Arquitetura Afetada

- backend: nao_aplicavel
- frontend: nao_aplicavel
- banco/migracoes: indice SQLite de PROJETOS (sync apos gravacoes)
- observabilidade: smoke local/remoto e auditorias documentais
- autorizacao/autenticacao: nao_aplicavel
- rollout: por Feature, User Story e Task com commits intermediarios conforme `GOV-COMMIT-POR-TASK.md`

## 11. Riscos Relevantes

- risco de produto: coexistencia prolongada entre superficies legadas e canonicas confundir operadores
- risco tecnico: wrappers e scripts permanecerem apontando para artefactos removidos
- risco operacional: smoke verde mascarar scaffold antigo ou SQLite estruturado vazio
- risco de dados: nao_aplicavel
- risco de adocao: consumidores historicos ainda dependerem de nomenclatura antiga

## 12. Nao-Objetivos

- Reescrever historico Git de projectos ja existentes no padrao antigo sem necessidade
- Alterar runtime, credenciais ou infraestrutura fora do toolkit OpenClaw

## 13. Contexto Especifico para Problema ou Refatoracao

- sintoma observado: o projecto permaneceu com PRD consolidado, mas sem intake coerente e com partes operacionais ainda legadas no bootstrap real
- impacto operacional: o gate `Intake -> PRD` ficou sem rastreabilidade formal, e scaffold/smoke/index podem continuar desalinhados do paradigma novo
- evidencia tecnica: [PRD-OPENCLAW-MIGRATION.md](./PRD-OPENCLAW-MIGRATION.md), [RELATORIO-AUDITORIA-MIGRATION-R01.md](./auditorias/RELATORIO-AUDITORIA-MIGRATION-R01.md) e [RELATORIO-AUDITORIA-MIGRATION-R02.md](./auditorias/RELATORIO-AUDITORIA-MIGRATION-R02.md)
- componente(s) afetado(s): `boot-prompt.md`, `SESSION-*`, skills OpenClaw, `scripts/criar_projeto.py`, `bin/check-openclaw-smoke.sh` e `scripts/openclaw_projects_index/`
- riscos de nao agir: o framework continua sem cadeia documental completa e o bootstrap real pode seguir validando o paradigma antigo

## 14. Lacunas Conhecidas

- migracao mecanica de todos os projectos legados do repositorio: fora do escopo desta rodada
- remocao definitiva das superficies legadas residuais: dependera de consumidores ainda activos
- qualquer dado historico nao reconstruivel com precisao: deve permanecer documentado como `nao_definido` em artefactos derivados futuros

## 15. Perguntas que o PRD Precisa Responder

- Como converter o scaffold, o smoke e o projecto smoke para a arvore canónica sem regressao?
- Como garantir que o SQLite v4 reflita projectos reais do framework, e nao apenas fixtures?
- Como blindar skills, review, auditoria e remediacao contra regressao semantica?

## 16. Checklist de Prontidao para PRD

- [x] intake_kind esta definido
- [x] source_mode esta definido
- [x] rastreabilidade de origem esta declarada ou marcada como nao_aplicavel
- [x] problema esta claro
- [x] publico principal esta claro
- [x] fluxo principal esta descrito
- [x] escopo dentro/fora esta fechado
- [x] metricas de sucesso estao declaradas
- [x] restricoes estao declaradas
- [x] dependencias e integracoes estao declaradas
- [x] arquitetura afetada esta mapeada
- [x] riscos relevantes estao declarados
- [x] lacunas conhecidas estao declaradas
- [x] contexto especifico de problema/refatoracao foi preenchido quando aplicavel
