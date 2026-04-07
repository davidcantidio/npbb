---
doc_id: "PRD-LEAN-BUNDLE-ATIVOS-CANDIDATE-PLAN"
version: "1.0"
status: "approved"
owner: "PM"
last_updated: "2026-04-03"
project: "LEAN-BUNDLE-ATIVOS-CANDIDATE-PLAN"
---

# PRD - LEAN-BUNDLE-ATIVOS-CANDIDATE-PLAN

## 0. Rastreabilidade

- **Intake de origem**: [INTAKE-LEAN-BUNDLE-ATIVOS-CANDIDATE-PLAN.md](./INTAKE-LEAN-BUNDLE-ATIVOS-CANDIDATE-PLAN.md)

## 1. Resumo Executivo

- **Nome do projeto**: LEAN-BUNDLE-ATIVOS-CANDIDATE-PLAN
- **Tese em 1 frase**: pipeline lean PRD para features

## 2. Especificacao Funcional

### 2.4 Escopo

### Dentro

- configuracao por evento das categorias iniciais `pista`, `pista premium` e `camarote`, com suporte a eventos que usem apenas parte do catalogo.
- dois modos canonicos de fornecimento: `interno_emitido_com_qr` e `externo_recebido`.
- reconciliacao entre quantidade `planejado` e quantidade `recebido_confirmado`.
- regra de prevalencia do `recebido_confirmado` para ativos originados em ticketeira.
- bloqueio operacional para aumentos dependentes de ticketeira ate o recebimento correspondente.
- emissao de ingressos internos unitarios com QR unico por destinatario, persistindo identidade suficiente para validacao futura de uso unico.
- persistencia e rastreabilidade de arquivos compartilhados, ingressos unitarios externos, links de drive e instrucoes textuais recebidas.
- fluxo de distribuicao, remanejamento, aumento, reducao, reenvio e registro de problemas operacionais.
- dashboard de ativos dentro do modulo Dashboard, seguindo o padrao visual e estrutural ja adotado no dashboard de leads.
- contratos de API e dados suficientes para integracao com skill externa de leitura de emails, sem construir a skill neste repositorio.

### Fora

- migrar provider runtime

## 2.5 Resultado de Negocio e Metricas

- objetivo principal: reduzir retrabalho documental
- metricas leading: tempo de decomposicao do PRD
- metricas lagging: backlog valido sem drift
- criterio minimo para considerar sucesso: 3 features renderizadas sem erro

## 2.6 Restricoes e Guardrails

- restricoes tecnicas: markdown canonico
- restricoes operacionais: sem provider no hot path
- restricoes legais ou compliance: nao_aplicavel
- restricoes de prazo: iteracao unica
- restricoes de design ou marca: manter nomenclatura Fabrica

## 2.7 Dependencias e Integracoes

- sistemas internos impactados: PROJETOS e scripts/fabrica_core
- sistemas externos impactados: nao_aplicavel
- dados de entrada necessarios: PRD aprovado
- dados de saida esperados: FEATURE-*.md canonicamente renderizado

## 5. Riscos Globais

- risco de produto: recortes ficarem amplos demais
- risco tecnico: proposta JSON inconsistente
- risco operacional: projetos com backlog legado no PRD
- risco de dados: baixo
- risco de adocao: operadores seguirem fluxo manual antigo

## 8. Rollout e Comunicacao

- estrategia de deploy: uso interno via CLI
- comunicacao de mudancas: registrar na governanca
- treinamento necessario: operadores da Fabrica
- suporte pos-launch: revisar feedback do hot path lean
