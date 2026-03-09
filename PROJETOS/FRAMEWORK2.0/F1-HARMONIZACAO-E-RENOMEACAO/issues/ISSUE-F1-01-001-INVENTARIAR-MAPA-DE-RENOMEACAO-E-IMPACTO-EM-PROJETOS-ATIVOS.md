---
doc_id: "ISSUE-F1-01-001-INVENTARIAR-MAPA-DE-RENOMEACAO-E-IMPACTO-EM-PROJETOS-ATIVOS.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-09"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F1-01-001 - Inventariar mapa de renomeacao e impacto em projetos ativos

## User Story

Como responsavel pelo framework, quero listar o mapa completo de renomeacao e o
blast radius nos projetos ativos para executar a mudanca sem quebrar referencias essenciais.

## Contexto Tecnico

Esta issue prepara a renomeacao de `PROJETOS/COMUM/` identificando nomes
antigos, nomes novos e os projetos ativos que precisam de correcao.

## Plano TDD

- Red: localizar referencias antigas e confirmar o impacto em projetos ativos.
- Green: consolidar o mapa de renomeacao e a lista de arquivos afetados.
- Refactor: revisar a ordem de aplicacao para reduzir drift.

## Criterios de Aceitacao

- Given os artefatos comuns atuais, When o inventario for concluido, Then existe mapa `nome antigo -> nome novo` para cada arquivo de `COMUM`
- Given os projetos ativos, When a leitura for encerrada, Then o impacto obrigatorio em `FRAMEWORK2.0`, `PILOTO-ISSUE-FIRST` e `dashboard-leads-etaria` esta explicitado
- Given a renomeacao futura, When a issue for usada como insumo, Then a ordem minima de aplicacao esta clara

## Definition of Done da Issue

- [x] mapa de renomeacao consolidado
- [x] projetos ativos impactados listados
- [x] ordem minima de aplicacao registrada

## Tasks Decupadas

- [x] T1: listar arquivos antigos de `PROJETOS/COMUM/` e seus nomes alvo
- [x] T2: localizar referencias obrigatorias nos projetos ativos
- [x] T3: registrar a ordem de aplicacao para a renomeacao

## Inventario Consolidado do Mapa de Renomeacao

`PROJETOS/COMUM/` hoje expoe 24 arquivos canonicos. O mapa abaixo consolida o
rename planejado no PRD contra o estado real observado no diretorio, separando
o que ainda e rename legado do que ja nasce ou permanece na convencao final.

| Nome antigo ou origem de referencia | Nome canonico alvo | Classificacao | Estado real em `PROJETOS/COMUM/` |
|---|---|---|---|
| `scrum-framework-master.md` | `GOV-FRAMEWORK-MASTER.md` | `renomear` | somente o nome canonico foi localizado |
| `SCRUM-GOV.md` | `GOV-SCRUM.md` | `renomear` | somente o nome canonico foi localizado |
| `AUDITORIA-GOV.md` | `GOV-AUDITORIA.md` | `renomear` | somente o nome canonico foi localizado |
| `INTAKE-FRAMEWORK.md` | `GOV-INTAKE.md` | `renomear` | somente o nome canonico foi localizado |
| `SPRINT-LIMITS.md` | `GOV-SPRINT-LIMITES.md` | `renomear` | somente o nome canonico foi localizado |
| `WORK-ORDER-SPEC.md` | `GOV-WORK-ORDER.md` | `renomear` | somente o nome canonico foi localizado |
| `DECISION-PROTOCOL.md` | `GOV-DECISOES.md` | `renomear` | somente o nome canonico foi localizado |
| `ISSUE-FIRST-TEMPLATES.md` | `GOV-ISSUE-FIRST.md` | `renomear` | somente o nome canonico foi localizado |
| `INTAKE-TEMPLATE.md` | `TEMPLATE-INTAKE.md` | `renomear` | somente o nome canonico foi localizado |
| `AUDITORIA-REPORT-TEMPLATE.md` | `TEMPLATE-AUDITORIA-RELATORIO.md` | `renomear` | somente o nome canonico foi localizado |
| `AUDITORIA-LOG-TEMPLATE.md` | `TEMPLATE-AUDITORIA-LOG.md` | `renomear` | somente o nome canonico foi localizado |
| `TASK_INSTRUCTIONS_SPEC.md` | `SPEC-TASK-INSTRUCTIONS.md` | `renomear` | somente o nome canonico foi localizado |
| `ANTI-MONOLITH-SPEC.md` | `SPEC-ANTI-MONOLITO.md` | `novo` | arquivo canonico novo localizado |
| `PROMPT-INTAKE-PARA-PRD.md` | `PROMPT-INTAKE-PARA-PRD.md` | `mantem` | arquivo ja estava canonico e localizado |
| `AUDITORIA-PROMPT.md` | `PROMPT-AUDITORIA.md` | `renomear` | somente o nome canonico foi localizado |
| `prompt_epicos_issues.md` | `PROMPT-PLANEJAR-FASE.md` | `renomear` | somente o nome canonico foi localizado |
| `PROMPT-MONOLITH-TO-INTAKE.md` | `PROMPT-MONOLITO-PARA-INTAKE.md` | `novo` | arquivo canonico novo localizado |
| `TEMPLATE - SESSION-INTAKE.md` | `SESSION-CRIAR-INTAKE.md` | `renomear` | somente o nome canonico foi localizado |
| `SESSION-CRIAR-PRD.md` | `SESSION-CRIAR-PRD.md` | `novo` | arquivo novo ja criado no nome final |
| `TEMPLATE - SESSION-PLAN.md` | `SESSION-PLANEJAR-PROJETO.md` | `renomear` | somente o nome canonico foi localizado |
| `SESSION-IMPLEMENT.md` | `SESSION-IMPLEMENTAR-ISSUE.md` | `novo` | arquivo canonico novo localizado |
| `SESSION-AUDIT.md` | `SESSION-AUDITAR-FASE.md` | `novo` | arquivo canonico novo localizado |
| `SESSION-REFACTOR.md` | `SESSION-REFATORAR-MONOLITO.md` | `novo` | arquivo canonico novo localizado |
| `SESSION-PROMPTS-MAP.md` | `SESSION-MAPA.md` | `renomear` | somente o nome canonico foi localizado |

Notas do inventario:

- `boot-prompt.md` permanece fora deste mapa porque vive em `PROJETOS/` e nao em `PROJETOS/COMUM/`.
- Os itens marcados como `mantem` ou `novo` entram no inventario para evitar rename indevido nas issues seguintes.

## Blast Radius Obrigatorio em Projetos Ativos

| Projeto | Arquivos/artefatos que exigem leitura na passada de renomeacao | Situacao atual | Regra para as proximas issues |
|---|---|---|---|
| `FRAMEWORK2.0` | `SESSION-PLANEJAR-PROJETO-Projeto-completo.md`, `PRD-FRAMEWORK2.0.md` | o prompt local ja aponta para `PROJETOS/COMUM/PROMPT-PLANEJAR-FASE.md`; o PRD concentra mencoes historicas aos nomes legados | `ISSUE-F1-01-003` fecha entrypoints; `ISSUE-F1-01-004` corrige apenas referencias operacionais remanescentes |
| `PILOTO-ISSUE-FIRST` | `DECISION-PROTOCOL.md`, `F1-VALIDACAO-DO-FRAMEWORK/issues/ISSUE-F1-01-001-ESTRUTURAR-PILOTO.md`, `F1-VALIDACAO-DO-FRAMEWORK/issues/ISSUE-F1-01-002-VALIDAR-NAVEGACAO-E-STATUS.md`, `feito/README.md` | os artefatos lidos ja referenciam `GOV-SCRUM`, `GOV-ISSUE-FIRST`, `GOV-SPRINT-LIMITES`, `GOV-WORK-ORDER` e `GOV-DECISOES` | manter como baseline; sem correcao obrigatoria identificada nesta passada |
| `dashboard-leads-etaria` | `DECISION-PROTOCOL.md`, `AUDIT-LOG.md` | os artefatos lidos ja referenciam `GOV-DECISOES.md` e `GOV-AUDITORIA.md` | manter como baseline; sem correcao obrigatoria identificada nesta passada |

Residuo historico deliberado:

- `PROJETOS/FRAMEWORK2.0/PRD-FRAMEWORK2.0.md` ainda cita nomes legados como parte da critica e do proprio mapa de renomeacao; esse arquivo nao deve receber rename mecanico nesta issue.

## Ordem Minima de Aplicacao

1. `ISSUE-F1-01-001` fixa o inventario, o conjunto de nomes finais e a separacao entre `renomear`, `mantem` e `novo`.
2. `ISSUE-F1-01-002` executa a passada em `PROJETOS/COMUM/`, renomeando apenas os itens classificados como `renomear` e alinhando referencias internas entre arquivos comuns.
3. `ISSUE-F1-01-003` atualiza `PROJETOS/boot-prompt.md` e `PROJETOS/COMUM/SESSION-MAPA.md` depois que os nomes finais estiverem estaveis no diretorio comum.
4. `ISSUE-F1-01-004` fecha somente referencias operacionais remanescentes em `FRAMEWORK2.0`, `PILOTO-ISSUE-FIRST` e `dashboard-leads-etaria`.
5. Mencoes historicas de analise, como as do `PRD-FRAMEWORK2.0.md`, so devem ser reescritas com decisao explicita; nao entram no rename mecanico.

## Validacao Documental

- `rg --files PROJETOS/COMUM | wc -l` retornou `24`, confirmando o conjunto atual de arquivos canonicos em `PROJETOS/COMUM/`.
- A busca por nomes legados nos tres projetos ativos retornou somente residuos historicos em `PROJETOS/FRAMEWORK2.0/PRD-FRAMEWORK2.0.md`; nao foram encontrados nomes antigos operacionais em `PILOTO-ISSUE-FIRST` nem em `dashboard-leads-etaria`.
- As referencias operacionais lidas para o blast radius ja navegam por nomes `GOV-*`, `PROMPT-*` e `SESSION-*`, com excecao deliberada do PRD historico do proprio `FRAMEWORK2.0`.

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/`
- `PROJETOS/boot-prompt.md`
- `PROJETOS/FRAMEWORK2.0/`
- `PROJETOS/PILOTO-ISSUE-FIRST/`
- `PROJETOS/dashboard-leads-etaria/`

## Artifact Minimo

- `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/EPIC-F1-01-RENOMEACAO-PARA-CONVENCAO-DE-PREFIXO.md`

## Dependencias

- [Epic](../EPIC-F1-01-RENOMEACAO-PARA-CONVENCAO-DE-PREFIXO.md)
- [Fase](../F1_FRAMEWORK2_0_EPICS.md)
- [PRD](../../PRD-FRAMEWORK2.0.md)
