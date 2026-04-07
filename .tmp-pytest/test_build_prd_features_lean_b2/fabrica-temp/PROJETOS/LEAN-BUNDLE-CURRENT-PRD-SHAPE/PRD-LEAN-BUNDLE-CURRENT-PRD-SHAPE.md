---
doc_id: "PRD-LEAN-BUNDLE-CURRENT-PRD-SHAPE"
version: "1.0"
status: "approved"
owner: "PM"
last_updated: "2026-04-05"
project: "LEAN-BUNDLE-CURRENT-PRD-SHAPE"
---

# PRD - LEAN-BUNDLE-CURRENT-PRD-SHAPE

## 1. Resumo Executivo

- **Nome do projeto**: LEAN-BUNDLE-CURRENT-PRD-SHAPE
- **Tese em 1 frase**: validar compatibilidade do bundler lean

## 2. Especificacao Funcional

### 2.5 Escopo

#### Dentro

- capability one
- capability two

#### Fora

- item fora do v1

### 2.6 Resultado de Negocio e Metricas

- objetivo principal: reduzir bloqueios espurios
- metricas leading: bundle com evidencias nao vazias
- metricas lagging: candidate plan gerado sem reparo manual
- criterio minimo para considerar sucesso: bundle lean preenchido

### 2.7 Restricoes e Guardrails

- restricoes tecnicas: preservar contrato atual do CLI
- restricoes operacionais: nao reescrever o PRD
- restricoes legais ou compliance: nao_aplicavel
- restricoes de prazo: correcao pontual
- restricoes de design ou marca: manter formato canonico do manifesto

### 2.8 Dependencias e Integracoes

- sistemas internos impactados: scripts/fabrica_core
- sistemas externos impactados: provider lean
- dados de entrada necessarios: PRD aprovado
- dados de saida esperados: bundle com evidencias e candidate plan

## 5. Riscos Globais

- risco tecnico: headings novos nao serem reconhecidos
- risco operacional: proposta bloqueada por bundle vazio

## 8. Rollout e Comunicacao

- estrategia de deploy: uso interno via CLI
- comunicacao de mudancas: registrar compatibilidade do bundler
- treinamento necessario: nao_aplicavel
- suporte pos-launch: observar bundle-only
