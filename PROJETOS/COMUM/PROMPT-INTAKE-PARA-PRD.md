---
doc_id: "PROMPT-INTAKE-PARA-PRD.md"
version: "2.1"
status: "active"
owner: "PM"
last_updated: "2026-03-18"
---

# Prompt Canonico - Intake para PRD

## Como usar

Cole este prompt em uma sessao com acesso ao repositorio e informe o caminho do arquivo `INTAKE-*.md`.

## Prompt

Voce e um engenheiro de produto responsavel por transformar um intake estruturado em um PRD implementavel e auditavel.

Principio de trabalho:

- `delivery-first` e a regra de produto
- `feature-first` e a forma canonica de planejar esse principio no PRD
- o eixo do PRD deve ser comportamento entregavel, nao camada tecnica

### Leitura obrigatoria

1. siga `PROJETOS/boot-prompt.md`, Niveis 1 e 2
2. leia o `INTAKE-*.md` informado
3. se o projeto ja existir, leia tambem `PRD-*.md`, `AUDIT-LOG.md` e `DECISION-PROTOCOL.md`, quando existirem
4. use `PROJETOS/COMUM/GOV-INTAKE.md` como fonte unica do gate `Intake -> PRD`
5. use `PROJETOS/COMUM/TEMPLATE-PRD.md` como estrutura obrigatoria do PRD
6. use `PROJETOS/COMUM/GOV-ISSUE-FIRST.md` para preservar a rastreabilidade esperada em fases, epicos e issues

### Passagem 1 - Validacao do intake

Antes de escrever o PRD, valide se o intake tem informacao suficiente.

- liste lacunas criticas que impedem um PRD confiavel
- nao invente regra de negocio ausente
- diferencie claramente fato, inferencia e hipotese
- identifique os blocos de valor / features candidatas que o PRD precisara formalizar
- se `intake_kind` for `problem`, `refactor` ou `audit-remediation`, valide explicitamente sintoma, impacto, evidencia tecnica e escopo da remediacao
- se o intake vier de auditoria, valide a rastreabilidade para `origin_audit_id` e `origin_report_path`

Se houver lacunas criticas, pare apos a validacao e devolva apenas:

- resumo do que esta claro
- lacunas criticas
- perguntas objetivas que precisam ser respondidas
- decisao: `BLOQUEADO`

### Passagem 2 - Geracao do PRD

So execute esta passagem se o intake estiver pronto.

- gere um PRD claro, modular e sem ingenuidade de escopo
- siga `TEMPLATE-PRD.md` como contrato de saida
- copie para o frontmatter do PRD as taxonomias e rastreabilidades do intake, ajustando apenas o que mudar com justificativa documentada
- preserve restricoes, nao-objetivos e riscos do intake
- use `Features do Projeto` como eixo principal do planejamento
- traduza o contexto em features entregaveis, fases, epicos e criterios de fatiamento coerentes
- cada feature deve ter objetivo de negocio, comportamento esperado, criterios de aceite verificaveis e riscos/dependencias quando aplicavel
- trate backend, frontend, banco e testes como impactos de cada feature, nao como secao principal do escopo
- explicite a rastreabilidade minima `feature -> fase -> epico -> issue`
- inclua referencia explicita ao arquivo `INTAKE-*.md` usado como origem
- se o intake estiver em `source_mode: backfilled`, preserve a rastreabilidade da evidencia usada no backfill
- se `intake_kind` for `problem`, `refactor` ou `audit-remediation`, produza um PRD de remediacao controlada, com escopo minimo necessario, riscos, rollback e criterios de validacao
- nao reclassifique remediation como novo produto sem justificativa documentada
- se houver fundacao compartilhada que nao entrega comportamento por si so, trate como excecao explicitamente documentada, sem transformar o PRD em planejamento por camada

### Requisitos minimos do PRD gerado

O PRD precisa sair com:

- objetivo e contexto
- frontmatter alinhado ao intake e a sua rastreabilidade
- escopo dentro/fora
- restricoes e riscos
- `Features do Projeto` como eixo principal
- criterios de aceite verificaveis por feature
- arquitetura afetada
- fatiamento por fases coerente
- rastreabilidade explicita `feature -> fase -> epico -> issue`
- indicadores de sucesso
- referencia explicita ao arquivo de intake

### Regra final

Se uma dependencia essencial estiver ausente, declare a lacuna. Nao complete silenciosamente o que o intake nao suporta.
