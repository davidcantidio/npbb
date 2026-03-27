---
doc_id: "PRD-TESTE-FW.md"
version: "1.0"
status: "draft"
owner: "PM"
last_updated: "2026-03-25"
project: "TESTE-FW"
intake_kind: "new-product"
source_mode: "original"
origin_project: "nao_aplicavel"
origin_phase: "nao_aplicavel"
origin_audit_id: "nao_aplicavel"
origin_report_path: "nao_aplicavel"
product_type: "platform-capability"
delivery_surface: "docs-governance"
business_domain: "governanca"
criticality: "media"
data_sensitivity: "interna"
integrations:
- "PROJETOS/COMUM"
change_type: "nova-capacidade"
audit_rigor: "standard"
---

> **STATUS: PENDENTE - aguardando conclusao do Intake**
>
> Este arquivo nasce como scaffold inicial. Antes de planejar fases reais
> do projeto, ele deve ser reescrito a partir do intake concreto.

# PRD - TESTE-FW

> Origem: [INTAKE-TESTE-FW.md](INTAKE-TESTE-FW.md)
>
> Este PRD descreve o scaffold canônico do projeto, nao um produto de negocio
> final. A intencao e deixar o projeto pronto para intake -> PRD -> planejamento
> sem confundir o placeholder inicial com backlog real.

## 0. Rastreabilidade

- **Intake de origem**: [INTAKE-TESTE-FW.md](INTAKE-TESTE-FW.md)
- **Versao do intake**: 1.0
- **Data de criacao**: 2026-03-25
- **PRD derivado**: nao aplicavel

## 1. Resumo Executivo

- **Nome do projeto**: TESTE-FW
- **Tese em 1 frase**: criar um projeto pronto para planejamento e execucao sem preenchimento manual dos cabecalhos principais
- **Valor esperado em 3 linhas**:
  - intake, PRD, audit log e wrappers locais prontos
  - primeira fase, epico e issue bootstrap gerados
  - menos drift e menor tempo de arranque para o projeto

## 2. Problema ou Oportunidade

- **Problema atual**: iniciar um projeto manualmente cria inconsistencias de nomes, caminhos e metadados
- **Evidencia do problema**: os artefatos de projeto exigem varios campos repetidos e faceis de esquecer
- **Custo de nao agir**: o primeiro ciclo do projeto comeca com drift documental e retrabalho
- **Por que agora**: o scaffold foi solicitado como ponto de partida oficial do novo projeto

## 3. Publico e Operadores

- **Usuario principal**: PM e engenheiro que vao planejar o projeto
- **Usuario secundario**: revisor ou auditor do fluxo de projeto
- **Operador interno**: script `scripts/criar_projeto.py`
- **Quem aprova ou patrocina**: PM

## 4. Jobs to be Done

- **Job principal**: criar um projeto novo pronto para planejamento e execucao
- **Jobs secundarios**: preencher cabecalhos comuns, evitar drift de nomes e publicar o bootstrap inicial
- **Tarefa atual que sera substituida**: montar a estrutura do projeto manualmente

## 5. Escopo

### Dentro

- scaffold inicial do projeto
- wrappers de sessao prontos para uso
- fase bootstrap com issue granularizada

### Fora

- features de negocio reais do projeto
- implementacao de codigo de produto
- deploy ou integrações externas

## 6. Resultado de Negocio e Metricas

- **Objetivo principal**: reduzir o custo de arranque de novos projetos
- **Metricas leading**: numero de campos prefillados; numero de placeholders manuais restantes
- **Metricas lagging**: tempo para iniciar o planejamento; numero de ajustes de drift no bootstrap
- **Criterio minimo para considerar sucesso**: o projeto nasce com docs e wrappers prontos para uso

## 7. Restricoes e Guardrails

- **Restricoes tecnicas**: manter nomes canônicos e caminhos repo-relative
- **Restricoes operacionais**: nao exigir preenchimento manual dos cabecalhos principais
- **Restricoes legais ou compliance**: nenhuma
- **Restricoes de prazo**: nenhuma
- **Restricoes de design ou marca**: nenhuma

## 8. Dependencias e Integracoes

- **Sistemas internos impactados**: `PROJETOS/COMUM` e o proprio scaffold do projeto
- **Sistemas externos impactados**: nao aplicavel
- **Dados de entrada necessarios**: nome do projeto e defaults de planejamento
- **Dados de saida esperados**: docs preenchidos, wrappers prontos e bootstrap inicial

## 9. Arquitetura Geral do Projeto

> Visao geral de impacto arquitetural (detalhes por feature na secao Features)

- **Backend**: nao aplicavel
- **Frontend**: nao aplicavel
- **Banco/migracoes**: nao aplicavel
- **Observabilidade**: audit log e relatorio base de fase
- **Autorizacao/autenticacao**: nao aplicavel
- **Rollout**: uso local do scaffold gerado

## 10. Riscos Globais

- **Risco de produto**: baixo, porque o objetivo e estrutural
- **Risco tecnico**: drift entre nome do arquivo, doc_id e caminhos
- **Risco operacional**: wrappers ainda exigirem ajustes manuais se a geracao falhar
- **Risco de dados**: nenhum
- **Risco de adocao**: o PM ainda pode preferir um bootstrap sem defaults

## 11. Nao-Objetivos

- nao definir features de negocio reais
- nao implementar codigo de aplicacao
- nao executar deploy

## 12. Features do Projeto

### Feature 1: Fundacao do projeto

#### Objetivo de Negocio

Entregar um scaffold canônico do projeto que reduza o arranque manual e deixe os artefatos de base prontos para uso.

#### Comportamento Esperado

O PM cria um projeto novo, abre os wrappers locais e segue o fluxo sem preencher manualmente os cabecalhos principais.

#### Criterios de Aceite

- intake, PRD, audit log e wrappers locais sao gerados com caminhos repo-relative
- fase F1-FUNDACAO, epic e issue bootstrap existem e apontam para Feature 1
- nao existem placeholders de frontmatter nem drifts entre doc_id e nome do arquivo

#### Dependencias com Outras Features

- nenhuma

#### Riscos Especificos

- drift de nomes e caminhos se a geracao nao for testada

#### Fases de Implementacao

1. Modelagem e scaffold: gerar docs e metadados.
2. Wrappers de sessao: preencher caminhos e defaults.
3. Issue bootstrap: criar issue granularizada e task.
4. Testes: validar tree, nomes e doc_ids.

#### Impacts

| Camada | Impacto | Detalhamento |
|---|---|---|
| Banco | nao aplicavel | nenhuma migracao |
| Backend | scripts/criar_projeto.py | gerador local do scaffold |
| Frontend | nao aplicavel | nenhum impacto |
| Testes | tests/test_criar_projeto.py | cobertura do scaffold e dos wrappers |

#### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---|---|---|---|
| T1 | Gerar docs base e metadados do projeto | 2 | - |
| T2 | Gerar wrappers locais e bootstrap F1 | 3 | T1 |
| T3 | Validar tree final, links e doc_ids | 2 | T2 |

## 13. Estrutura de Fases

## Fase 1: F1-FUNDACAO

- **Objetivo**: consolidar o scaffold inicial do projeto.
- **Features incluídas**: Feature 1
- **Gate de saída**: o projeto novo esta pronto para planejamento e execucao sem drift documental.
- **Critérios de aceite**:
  - intake, PRD, audit log e wrappers locais existem
  - a fase bootstrap possui epico, issue e task
  - os caminhos sao repo-relative

### Épicos da Fase 1

| Epico | Feature(s) | Status | SP Total |
|---|---|---|---|
| EPIC-F1-01 | Feature 1 | todo | 7 |

## 14. Epicos

### Épico: Fundacao do projeto

- **ID**: EPIC-F1-01
- **Fase**: F1
- **Feature de Origem**: Feature 1
- **Objetivo**: entregar o scaffold inicial e validar os artefatos de base.
- **Resultado de Negócio Mensurável**: o projeto pode iniciar planejamento e execucao sem preenchimento manual dos cabecalhos principais.
- **Contexto Arquitetural**: raiz do projeto pronta para fases futuras; wrappers locais apontando para caminhos repo-relative.
- **Definition of Done**:
  - [ ] intake e PRD existem com frontmatter preenchido
  - [ ] wrappers de sessao estao completos
  - [ ] fase F1, epico, issue e task existem
  - [ ] audit log aponta para o bootstrap inicial

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature |
|---|---|---|---|---|
| ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO | Estabilizar scaffold inicial do projeto | 3 | todo | Feature 1 |

## 15. Dependencias Externas

| Dependencia | Tipo | Origem | Impacto | Status |
|---|---|---|---|---|
| PROJETOS/COMUM | docs-governance | framework | fonte canônica do scaffold | active |

## 16. Rollout e Comunicacao

- **Estratégia de deploy**: uso local do scaffold gerado
- **Comunicação de mudanças**: o PM recebe os wrappers prontos e os caminhos canônicos
- **Treinamento necessário**: nenhum
- **Suporte pós-launch**: ajuste do scaffold caso o projeto real exija novas fases

## 17. Revisões e Auditorias

- **Auditorias planejadas**: F1-R01
- **Critérios de auditoria**: aderencia ao scaffold, rastreabilidade e ausencia de drift
- **Threshold anti-monolito**: nao aplicavel; o artefato e documental

## 18. Checklist de Prontidão

- [x] Intake referenciado e versao confirmada
- [x] Features definidas com criterios de aceite verificaveis
- [x] Cada feature com impacts por camada preenchidos
- [x] Rastreabilidade explicita `Feature -> Fase -> Epico -> Issue`
- [x] Épicos criados e vinculados a features
- [x] Fases definidas com gates de saída
- [x] Dependências externas mapeadas
- [x] Riscos identificados e mitigacoes planejadas
- [x] Rollout planejado

## 19. Anexos e Referências

- [Intake](INTAKE-TESTE-FW.md)
- [Audit Log](AUDIT-LOG.md)
- [Fase](F1-FUNDACAO/F1_TESTE-FW_EPICS.md)
- [Epic](F1-FUNDACAO/EPIC-F1-01-FUNDACAO-DO-PROJETO.md)
- [Issue bootstrap](F1-FUNDACAO/issues/ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO/README.md)
- [Relatorio de auditoria](F1-FUNDACAO/auditorias/RELATORIO-AUDITORIA-F1-R01.md)

> Frase Guia: "Feature organiza, Task executa, Teste valida"
