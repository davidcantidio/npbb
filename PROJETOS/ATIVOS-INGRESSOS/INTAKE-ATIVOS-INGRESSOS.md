---
doc_id: "INTAKE-ATIVOS-INGRESSOS"
version: "1.0"
status: "draft"
owner: "PM"
last_updated: "2026-04-06"
project: "ATIVOS-INGRESSOS"
intake_kind: "new-capability"
source_mode: "original"
origin_project: "nao_aplicavel"
origin_phase: "nao_aplicavel"
origin_audit_id: "nao_aplicavel"
origin_report_path: "nao_aplicavel"
product_type: "internal-framework"
delivery_surface: "cli-deterministica"
business_domain: "engenharia"
criticality: "media"
data_sensitivity: "interna"
integrations:
  - "Postgres"
  - "Markdown"
change_type: "nova-capacidade"
audit_rigor: "standard"
generated_by: "fabrica-cli"
generator_stage: "scaffold"
---

# INTAKE - ATIVOS-INGRESSOS

> Scaffold inicial lean da Fabrica. Preencha a ideia principal ou use `fabrica generate intake`.

## 0. Rastreabilidade de Origem

- projeto de origem: nao_aplicavel
- fase de origem: nao_aplicavel
- auditoria de origem: nao_aplicavel
- relatorio de origem: nao_aplicavel
- motivo da abertura deste intake: criar o projeto ATIVOS-INGRESSOS na Fabrica

## 1. Resumo Executivo

- nome curto da iniciativa: ATIVOS-INGRESSOS
- tese em 1 frase: nao_definido
- valor esperado em 3 linhas:
  - nao_definido
  - nao_definido
  - nao_definido

## 2. Problema ou Oportunidade

- problema atual: nao_definido
- evidencia do problema: nao_definido
- custo de nao agir: nao_definido
- por que agora: nao_definido

## 3. Publico e Operadores

- usuario principal: nao_definido
- usuario secundario: nao_definido
- operador interno: CLI Fabrica
- quem aprova ou patrocina: nao_definido

## 4. Jobs to be Done

- job principal: nao_definido
- jobs secundarios: nao_definido
- tarefa atual que sera substituida: nao_definido

## 5. Fluxo Principal Desejado

1. Criar o projeto.
2. Produzir intake e PRD.
3. Decompor em features, user stories e tasks.
4. Sincronizar o read model Postgres.

## 6. Escopo Inicial

### Dentro

- criar a cadeia documental minima do projeto
- manter sync Postgres obrigatorio no fluxo operacional

### Fora

- TUI
- host runtime

## 7. Resultado de Negocio e Metricas

- objetivo principal: criar um projeto operacional na Fabrica
- metricas leading: tempo de bootstrap do projeto
- metricas lagging: projeto refletido no banco e backlog gerado sem drift
- criterio minimo para considerar sucesso: o projeto existir em Markdown e no read model

## 8. Restricoes e Guardrails

- restricoes tecnicas: Markdown como fonte de verdade; Postgres como read model
- restricoes operacionais: fluxo deterministico por CLI
- restricoes legais ou compliance: nao_aplicavel
- restricoes de prazo: nao_definido
- restricoes de design ou marca: nome publico Fabrica

## 9. Dependencias e Integracoes

- sistemas internos impactados: `scripts/fabrica_projects_index/`, `PROJETOS/`
- sistemas externos impactados: Postgres
- dados de entrada necessarios: ideia inicial do projeto
- dados de saida esperados: intake, PRD, features, user stories, tasks

## 10. Arquitetura Afetada

- backend: read model Postgres
- frontend: nao_aplicavel
- banco/migracoes: tabelas do indice de projetos
- observabilidade: `sync_runs`
- autorizacao/autenticacao: nao_aplicavel
- rollout: CLI local

## 11. Riscos Relevantes

- risco de produto: escopo indefinido
- risco tecnico: drift entre docs e automacao
- risco operacional: sync falhar e ocultar o estado do projeto
- risco de dados: baixo
- risco de adocao: manutencao de fluxos legados fora do core

## 12. Nao-Objetivos

- reintroduzir wrappers locais por projeto
- acoplar o core ao host runtime
- esconder falhas de sync

## 13. Contexto Especifico para Problema ou Refatoracao

- sintoma observado: nao_aplicavel
- impacto operacional: nao_aplicavel
- evidencia tecnica: nao_aplicavel
- componente(s) afetado(s): nao_aplicavel
- riscos de nao agir: nao_aplicavel

## 14. Lacunas Conhecidas

- regra de negocio ainda nao definida: sim
- dependencia ainda nao confirmada: nao
- dado ainda nao disponivel: sim
- decisao de UX ainda nao fechada: nao_aplicavel
- outro ponto em aberto: detalhar a ideia inicial

## 15. Perguntas que o PRD Precisa Responder

- qual problema concreto o projeto resolve?
- quais comportamentos entregaveis devem virar features?
- quais validacoes minimas precisam existir?

## 16. Checklist de Prontidao para PRD

- [ ] tese principal definida
- [ ] escopo dentro/fora revisado
- [ ] metricas de sucesso declaradas
- [ ] riscos relevantes declarados
