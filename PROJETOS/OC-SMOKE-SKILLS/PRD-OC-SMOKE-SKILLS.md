---
doc_id: "PRD-OC-SMOKE-SKILLS.md"
version: "1.1"
status: "draft"
owner: "PM"
last_updated: "2026-03-23"
project: "OC-SMOKE-SKILLS"
intake_kind: "new-capability"
source_mode: "original"
origin_project: "nao_aplicavel"
origin_phase: "nao_aplicavel"
origin_audit_id: "nao_aplicavel"
origin_report_path: "PROJETOS/OC-SMOKE-SKILLS/GUIA-TESTE-SKILLS.md"
product_type: "platform-capability"
delivery_surface: "docs-governance"
business_domain: "governanca"
criticality: "media"
data_sensitivity: "interna"
integrations:
  - "PROJETOS/COMUM"
  - "openclaw-* skills"
  - "bin/check-openclaw-smoke.sh"
change_type: "nova-capacidade"
audit_rigor: "standard"
---

# PRD - OC-SMOKE-SKILLS

> Origem: [INTAKE-OC-SMOKE-SKILLS.md](PROJETOS/OC-SMOKE-SKILLS/INTAKE-OC-SMOKE-SKILLS.md)
>
> Este PRD trata `OC-SMOKE-SKILLS` como projeto-canario do framework, e nao como
> backlog de produto. A fonte primaria de aceite operacional e
> `GUIA-TESTE-SKILLS.md`.

## 0. Rastreabilidade

- **Intake de origem**: [INTAKE-OC-SMOKE-SKILLS.md](PROJETOS/OC-SMOKE-SKILLS/INTAKE-OC-SMOKE-SKILLS.md)
- **Versao do intake**: 1.1
- **Data de criacao**: 2026-03-23
- **PRD derivado**: nao aplicavel

## 1. Resumo Executivo

- **Nome do projeto**: OC-SMOKE-SKILLS
- **Tese em 1 frase**: manter um projeto minimo e controlado capaz de provar que a suite `openclaw-*` ainda respeita o framework atual ponta a ponta
- **Valor esperado em 3 linhas**:
  - regressao de framework aparece primeiro no canario
  - o ciclo `roteamento -> execucao -> revisao -> auditoria` fica demonstravel com baixo blast radius
  - `GUIA-TESTE-SKILLS.md` e `./bin/check-openclaw-smoke.sh` viram o contrato de prova minima

## 2. Problema ou Oportunidade

- **Problema atual**: mudancas em `PROJETOS/COMUM`, wrappers e no gerador podem quebrar a suite `openclaw-*` sem uma prova controlada e reproduzivel
- **Evidencia do problema**: o guia de teste ja descreve prompts, precondicoes e saidas esperadas, mas o PRD antigo ainda descrevia um scaffold generico
- **Custo de nao agir**: regressao do framework so aparece quando um projeto real falha
- **Por que agora**: a remodernizacao dos projetos precisa de um canario confiavel antes de mexer no backlog principal

## 3. Publico e Operadores

- **Usuario principal**: mantenedor do framework OpenClaw
- **Usuario secundario**: operador que instala skills localmente ou valida o gateway remoto
- **Operador interno**: suite `openclaw-*`, `boot-prompt.md`, wrappers locais e `./bin/check-openclaw-smoke.sh`
- **Quem aprova ou patrocina**: PM

## 4. Jobs to be Done

- **Job principal**: validar rapidamente se o framework ainda sabe ler o projeto, descobrir a unidade certa e obedecer aos gates do fluxo issue-first
- **Jobs secundarios**: checar smoke local/remoto; confirmar wrappers atuais; capturar drift antes de tocar projetos reais
- **Tarefa atual que sera substituida**: descobrir regressao de framework apenas em backlog real

## 5. Escopo

### Dentro

- roteamento e autonomia sobre um backlog canario controlado
- wrappers locais alinhados ao framework atual
- issue bootstrap usada para provar execucao, revisao e auditoria
- smoke local e remoto descrito no guia

### Fora

- backlog de produto proprio
- features de negocio fora do proprio framework OpenClaw
- qualquer entrega runtime que nao seja a validacao do canario

## 6. Resultado de Negocio e Metricas

- **Objetivo principal**: detectar regressao do framework cedo e com baixo custo
- **Metricas leading**: `./bin/check-openclaw-smoke.sh` verde; prompts do guia roteando corretamente; wrappers sem defaults obsoletos
- **Metricas lagging**: menor numero de regressões descobertas tardiamente em projetos reais
- **Criterio minimo para considerar sucesso**: o canario cobre o ciclo minimo do framework com evidencias reproduziveis

## 7. Restricoes e Guardrails

- **Restricoes tecnicas**: manter o projeto pequeno, documental e alinhado a `GUIA-TESTE-SKILLS.md`
- **Restricoes operacionais**: nao transformar o canario em backlog de produto; qualquer drift real deve ser corrigido no framework compartilhado
- **Restricoes legais ou compliance**: nenhuma
- **Restricoes de prazo**: acompanhar o framework no mesmo ciclo de mudanca
- **Restricoes de design ou marca**: nenhuma

## 8. Dependencias e Integracoes

- **Sistemas internos impactados**: `PROJETOS/COMUM`, wrappers locais, `scripts/criar_projeto.py`, `bin/check-openclaw-smoke.sh`
- **Sistemas externos impactados**: gateway remoto quando a trilha remota for exercida
- **Dados de entrada necessarios**: prompts do guia, artefatos do projeto, suite local das skills
- **Dados de saida esperados**: veredito rapido sobre aderencia do framework e evidencias para correcao

## 9. Arquitetura Geral do Projeto

- **Backend**: scripts de smoke e habilidades OpenClaw; nenhum codigo de produto
- **Frontend**: nao aplicavel
- **Banco/migracoes**: nao aplicavel
- **Observabilidade**: audit log, relatorio base de fase e saida do smoke
- **Autorizacao/autenticacao**: nao aplicavel
- **Rollout**: local primeiro; remoto opcional

## 10. Riscos Globais

- **Risco de produto**: baixo, porque o projeto e apenas canario
- **Risco tecnico**: canario envelhecer e mascarar drift
- **Risco operacional**: ignorar o canario e descobrir regressao apenas em backlog real
- **Risco de dados**: nenhum
- **Risco de adocao**: o canario perder o papel de prova minima e acumular escopo demais

## 11. Nao-Objetivos

- virar backlog principal da plataforma
- carregar features de negocio alheias ao framework
- substituir testes de produto

## 12. Features do Projeto

### Feature 1: Canario do framework OpenClaw

#### Objetivo de Negocio

Entregar uma prova minima e controlada de que o framework atual continua operando como esperado.

#### Comportamento Esperado

O mantenedor roda o guia de smoke, aciona as skills `openclaw-*` e observa o comportamento esperado sem depender de backlog real.

#### Criterios de Aceite

- `GUIA-TESTE-SKILLS.md` e o projeto concordam sobre prompts, precondicoes e saidas esperadas
- wrappers locais apontam para a issue e a fase canario corretas
- `./bin/check-openclaw-smoke.sh` cobre o smoke minimo do framework

#### Dependencias com Outras Features

- nenhuma

#### Riscos Especificos

- drift entre guia, wrappers e backlog bootstrap do canario

#### Fases de Implementacao

1. Remodernizar intake, PRD e wrappers locais.
2. Manter issue bootstrap como unidade canario de execucao controlada.
3. Validar smoke local e remoto.
4. Usar a evidencia do canario para corrigir o framework compartilhado.

#### Impacts

| Camada | Impacto | Detalhamento |
|---|---|---|
| Backend | `openclaw-*` + smoke scripts | roteamento e validacao do framework |
| Frontend | nao aplicavel | nenhum impacto |
| Testes | `bin/check-openclaw-smoke.sh` | smoke local/remoto do canario |

#### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---|---|---|---|
| T1 | Remodernizar docs e wrappers do canario | 3 | - |
| T2 | Executar a issue bootstrap como prova controlada | 3 | T1 |
| T3 | Revisar, auditar e rodar smoke do framework | 3 | T2 |

## 13. Estrutura de Fases

## Fase 1: F1-FUNDACAO

- **Objetivo**: validar o canario de framework OpenClaw.
- **Features incluidas**: Feature 1
- **Gate de saida**: o canario consegue provar o comportamento minimo esperado do framework sem drift documental.
- **Critérios de aceite**:
  - guia, intake, PRD e wrappers estao sincronizados
  - a issue bootstrap do canario foi executada, revisada e auditada quando aplicavel
  - o smoke do framework e reproduzivel

### Epicos da Fase 1

| Epico | Feature(s) | Status | SP Total |
|---|---|---|---|
| EPIC-F1-01 | Feature 1 | todo | 9 |

## 14. Epicos

### Epico: Canario do framework

- **ID**: EPIC-F1-01
- **Fase**: F1
- **Feature de Origem**: Feature 1
- **Objetivo**: manter uma prova minima e controlada de que o framework atual continua operando como esperado.
- **Resultado de Negocio Mensuravel**: regressao do framework aparece primeiro no canario e nao em backlog real.
- **Contexto Arquitetural**: projeto documental pequeno, wrappers locais atuais e smoke script versionado.
- **Definition of Done**:
  - [ ] intake, PRD e guia do canario estao alinhados
  - [ ] wrappers locais refletem a fila atual do canario
  - [ ] issue bootstrap continua rastreavel como prova controlada
  - [ ] smoke local do framework possui evidencia reproduzivel

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature |
|---|---|---|---|---|
| ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO | Estabilizar scaffold inicial do projeto-canario | 3 | todo | Feature 1 |

## 15. Dependencias Externas

| Dependencia | Tipo | Origem | Impacto | Status |
|---|---|---|---|---|
| PROJETOS/COMUM | docs-governance | framework | fonte canônica do canario | active |
| GUIA-TESTE-SKILLS.md | docs-governance | projeto local | contrato de aceite do smoke | active |

## 16. Rollout e Comunicacao

- **Estrategia de deploy**: smoke local sempre; remoto apenas quando o gateway tambem for validado
- **Comunicacao de mudancas**: drift encontrado aqui vira correcao do framework compartilhado
- **Treinamento necessario**: leitura do guia e dos wrappers locais
- **Suporte pos-launch**: manter o canario sincronizado com o framework atual

## 17. Revisoes e Auditorias

- **Auditorias planejadas**: F1-R01
- **Criterios de auditoria**: aderencia ao guia, rastreabilidade issue-first e ausencia de defaults obsoletos
- **Threshold anti-monolito**: nao aplicavel; o projeto e documental

## 18. Checklist de Prontidao

- [x] Intake referenciado e versao confirmada
- [x] Features definidas com criterios de aceite verificaveis
- [x] Cada feature com impacts por camada preenchidos
- [x] Rastreabilidade explicita `Feature -> Fase -> Epico -> Issue`
- [x] Epicos criados e vinculados a features
- [x] Fases definidas com gates de saida
- [x] Dependencias externas mapeadas
- [x] Riscos identificados e mitigacoes planejadas
- [x] Rollout planejado

## 19. Anexos e Referencias

- [Intake](PROJETOS/OC-SMOKE-SKILLS/INTAKE-OC-SMOKE-SKILLS.md)
- [Guia de teste](PROJETOS/OC-SMOKE-SKILLS/GUIA-TESTE-SKILLS.md)
- [Audit Log](PROJETOS/OC-SMOKE-SKILLS/AUDIT-LOG.md)
- [Fase](PROJETOS/OC-SMOKE-SKILLS/F1-FUNDACAO/F1_OC-SMOKE-SKILLS_EPICS.md)
- [Epic](PROJETOS/OC-SMOKE-SKILLS/F1-FUNDACAO/EPIC-F1-01-FUNDACAO-DO-PROJETO.md)
- [Issue bootstrap](PROJETOS/OC-SMOKE-SKILLS/F1-FUNDACAO/issues/ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO)
- [Relatorio de auditoria](PROJETOS/OC-SMOKE-SKILLS/F1-FUNDACAO/auditorias/RELATORIO-AUDITORIA-F1-R01.md)
