---
doc_id: "INTAKE-DL2.md"
version: "1.0"
status: "draft"
owner: "PM"
last_updated: "2026-03-18"
project: "DL2"
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

# INTAKE - DL2

> Scaffold inicial do projeto DL2 para que intake, PRD, wrappers e
> bootstrap de fase sejam criados sem preenchimento manual repetitivo.

## 0. Rastreabilidade de Origem

- projeto de origem: nao_aplicavel
- fase de origem: nao_aplicavel
- auditoria de origem: nao_aplicavel
- relatorio de origem: nao_aplicavel
- motivo da abertura deste intake: gerar um projeto novo com scaffold canônico e wrappers prontos para uso

## 1. Resumo Executivo

- nome curto da iniciativa: scaffold canônico do projeto
- tese em 1 frase: criar um projeto pronto para planejamento e execucao sem preencher manualmente os cabecalhos principais
- valor esperado em 3 linhas:
  - intake, PRD, audit log e wrappers locais prontos
  - primeira fase, epico e issue bootstrap gerados
  - menos drift e menor tempo de arranque para o projeto

## 2. Problema ou Oportunidade

- problema atual: iniciar um projeto manualmente cria inconsistencias de nomes, caminhos e metadados
- evidencia do problema: os artefatos de projeto exigem varios campos repetidos e faceis de esquecer
- custo de nao agir: o primeiro ciclo do projeto comeca com drift documental e retrabalho
- por que agora: o scaffold foi solicitado como ponto de partida oficial do novo projeto

## 3. Publico e Operadores

- usuario principal: PM e engenheiro que vao planejar o projeto
- usuario secundario: revisor ou auditor do fluxo de projeto
- operador interno: script `scripts/criar_projeto.py`
- quem aprova ou patrocina: PM

## 4. Jobs to be Done

- job principal: criar um projeto novo pronto para planejamento e execucao
- jobs secundarios: preencher cabecalhos comuns, evitar drift de nomes e publicar o bootstrap inicial
- tarefa atual que sera substituida: montar a estrutura do projeto manualmente

## 5. Fluxo Principal Desejado

Descreva o fluxo ponta a ponta em etapas curtas:

1. Informar o nome do projeto e os defaults de planejamento.
2. Gerar intake, PRD, audit log e wrappers locais com caminhos repo-relative.
3. Criar a fase F1-FUNDACAO com epico, issue granularizada e task.
4. Deixar o projeto pronto para planejamento, implementacao e auditoria.

## 6. Escopo Inicial

### Dentro

- scaffold inicial do projeto
- wrappers de sessao prontos para uso
- fase bootstrap com issue granularizada

### Fora

- features de negocio reais do projeto
- implementacao de codigo de produto
- deploy ou integrações externas

## 7. Resultado de Negocio e Metricas

- objetivo principal: reduzir o custo de arranque de novos projetos
- metricas leading: numero de campos prefillados; numero de placeholders manuais restantes
- metricas lagging: tempo para iniciar o planejamento; numero de ajustes de drift no bootstrap
- criterio minimo para considerar sucesso: o projeto nasce com docs e wrappers prontos para uso

## 8. Restricoes e Guardrails

- restricoes tecnicas: manter nomes canônicos e caminhos repo-relative
- restricoes operacionais: nao exigir preenchimento manual dos cabecalhos principais
- restricoes legais ou compliance: nenhuma
- restricoes de prazo: nenhuma
- restricoes de design ou marca: nenhuma

## 9. Dependencias e Integracoes

- sistemas internos impactados: `PROJETOS/COMUM` e o proprio scaffold do projeto
- sistemas externos impactados: nao aplicavel
- dados de entrada necessarios: nome do projeto e defaults de planejamento
- dados de saida esperados: docs preenchidos, wrappers prontos e bootstrap inicial

## 10. Arquitetura Afetada

- backend: nao aplicavel
- frontend: nao aplicavel
- banco/migracoes: nao aplicavel
- observabilidade: audit log e relatorio base de fase
- autorizacao/autenticacao: nao aplicavel
- rollout: uso local do scaffold gerado

## 11. Riscos Relevantes

- risco de produto: baixo, porque o objetivo e estrutural
- risco tecnico: drift entre nome do arquivo, doc_id e caminhos
- risco operacional: wrappers ainda exigirem ajustes manuais se a geracao falhar
- risco de dados: nenhum
- risco de adocao: o PM ainda pode preferir um bootstrap sem defaults

## 12. Nao-Objetivos

- nao definir features de negocio reais
- nao implementar codigo de aplicacao
- nao executar deploy

## 13. Contexto Especifico para Problema ou Refatoracao

- sintoma observado: projeto novo sem estrutura canônica
- impacto operacional: necessidade de preencher manualmente sessoes e docs
- evidencia tecnica: o gerador precisa criar wrappers, phase bootstrap e artefatos base
- componente(s) afetado(s): `scripts/criar_projeto.py`, `PROJETOS/COMUM` e os novos arquivos do projeto
- riscos de nao agir: cada novo projeto diverge do padrao e aumenta retrabalho

## 14. Lacunas Conhecidas

- nenhuma no nivel de scaffold
