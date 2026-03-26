---
doc_id: "PRD-DASHBOARD-ATIVOS.md"
version: "1.0"
status: "draft"
owner: "PM"
last_updated: "2026-03-26"
project: "DASHBOARD-ATIVOS"
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
> Este arquivo nasce como scaffold inicial. Antes de planejar features reais
> do projeto, ele deve ser reescrito a partir do intake concreto.

# PRD - DASHBOARD-ATIVOS

> Origem: [INTAKE-DASHBOARD-ATIVOS.md](INTAKE-DASHBOARD-ATIVOS.md)
>
> Este PRD descreve o scaffold canonico do projeto, nao um produto de negocio
> final. A intencao e deixar o projeto pronto para intake -> PRD -> decomposicao
> sem confundir o placeholder inicial com backlog real.

## 0. Rastreabilidade

- **Intake de origem**: [INTAKE-DASHBOARD-ATIVOS.md](INTAKE-DASHBOARD-ATIVOS.md)
- **Versao do intake**: 1.0
- **Data de criacao**: 2026-03-26
- **PRD derivado**: nao aplicavel

## 1. Resumo Executivo

- **Nome do projeto**: DASHBOARD-ATIVOS
- **Tese em 1 frase**: criar um projeto pronto para planejamento e execucao sem preenchimento manual dos cabecalhos principais
- **Valor esperado em 3 linhas**:
  - intake, PRD, audit log e wrappers locais prontos
  - feature bootstrap, user story bootstrap e task inicial geradas
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
- feature bootstrap com user story granularizada

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

> Visao unificada de impacto arquitetural em nivel de projeto. O detalhamento
> por entregavel acontece apos este PRD, na etapa `PRD -> Features`.

- **Backend**: nao aplicavel
- **Frontend**: nao aplicavel
- **Banco/migracoes**: nao aplicavel
- **Observabilidade**: audit log e relatorio base de feature
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

> **Pos-PRD (nao faz parte deste arquivo):** backlog estruturado de features,
> user stories e tasks segue `GOV-FEATURE.md`, `GOV-USER-STORY.md`,
> `GOV-SCRUM.md` e as sessoes `SESSION-DECOMPOR-*`.

## 12. Dependencias Externas

| Dependencia | Tipo | Origem | Impacto | Status |
|---|---|---|---|---|
| PROJETOS/COMUM | docs-governance | framework | fonte canonica do scaffold | active |

## 13. Rollout e Comunicacao

- **Estratégia de deploy**: uso local do scaffold gerado
- **Comunicacao de mudancas**: o PM recebe os wrappers prontos, o PRD placeholder e a indicacao explicita da proxima etapa `PRD -> Features`
- **Treinamento necessário**: nenhum
- **Suporte pos-launch**: ajuste do scaffold caso o projeto real exija novas features

## 14. Revisoes e Auditorias

- **Gates e auditorias em nivel de projeto**: preencher apos intake e PRD concretos; o bootstrap existe apenas para evitar drift inicial
- **Critérios de auditoria**: aderencia ao scaffold, rastreabilidade e ausencia de drift
- **Threshold anti-monolito**: nao aplicavel; o artefato e documental

## 15. Checklist de Prontidao

- [ ] Intake referenciado e versao confirmada
- [ ] Problema, escopo, restricoes, riscos e metricas preenchidos de forma verificavel
- [ ] Arquitetura geral e rollout descritos sem catalogo de features nem tabelas de user stories neste PRD
- [ ] Dependencias externas mapeadas
- [ ] Proxima etapa explicita: `PRD -> Features` via `SESSION-DECOMPOR-PRD-EM-FEATURES.md` / `PROMPT-PRD-PARA-FEATURES.md`

## 16. Anexos e Referencias

- [Intake](INTAKE-DASHBOARD-ATIVOS.md)
- [Audit Log](AUDIT-LOG.md)
- [Feature bootstrap](features/FEATURE-1-FOUNDATION/FEATURE-1.md)
- [User Story bootstrap](features/FEATURE-1-FOUNDATION/user-stories/US-1-01-BOOTSTRAP/README.md)
- [Relatorio de auditoria](features/FEATURE-1-FOUNDATION/auditorias/RELATORIO-AUDITORIA-F1-R01.md)
- [Relatorio de encerramento](encerramento/RELATORIO-ENCERRAMENTO.md)

> Frase Guia: "PRD direciona, Feature organiza, User Story fatia, Task executa, Teste valida"
