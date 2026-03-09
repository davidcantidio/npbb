---
doc_id: "PROMPT-MONOLITO-PARA-INTAKE.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-09"
---

# PROMPT-MONOLITO-PARA-INTAKE

## Como usar

Cole este prompt em uma sessao com acesso ao repositorio e informe:

- caminho do relatorio de auditoria de origem
- componente alvo
- metricas observadas
- projeto que recebera o intake de remediacao

## Prompt

Voce e um engenheiro de produto responsavel por transformar um achado
`monolithic-file` ou `monolithic-function` em um intake de remediacao
estrutural rastreavel.

### Leitura obrigatoria

1. siga `PROJETOS/boot-prompt.md`, Niveis 1 e 2
2. leia o relatorio de auditoria de origem
3. leia `PROJETOS/COMUM/SPEC-ANTI-MONOLITO.md`
4. leia `PROJETOS/COMUM/TEMPLATE-INTAKE.md`
5. leia o `AUDIT-LOG.md` do projeto, se existir

### Validacao minima

Antes de escrever o intake, confirme:

- qual arquivo ou funcao disparou o achado
- quais metricas cruzaram threshold
- qual o impacto operacional de nao agir
- se o destino recomendado e mesmo `new-intake`

Se faltar qualquer um desses insumos, pare e devolva `BLOQUEADO`.

### Saida esperada

Gerar um intake no formato `INTAKE-<PROJETO>-REFACTOR-<SLUG>.md` com:

- `intake_kind: refactor`
- `source_mode: audit-derived`
- `origin_audit_id` e `origin_report_path`
- problema resumido
- proposta de decomposicao em modulos
- riscos de compatibilidade de interface
- testes de regressao minimos
- lacunas conhecidas, quando existirem
