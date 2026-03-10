---
doc_id: "SESSION-REMEDIAR-HOLD.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-10"
---

# SESSION-REMEDIAR-HOLD — Roteamento de Remediação Pós-Auditoria

## Quando usar

Use este prompt imediatamente após qualquer auditoria com veredito `hold`,
independente de como o relatório foi produzido (agente autônomo, sessão de chat
ou auditor externo). Cobre todos os destinos canônicos de follow-up em um único
fluxo guiado.

Não use para auditorias com veredito `go` ou `cancelled`.

## Parâmetros obrigatórios

Preencha e cole junto com este prompt:

```
PROJETO:        <nome canônico do projeto, ex: FRAMEWORK2.0>
FASE:           <identificador da fase, ex: F1>
RELATORIO_PATH: <caminho do relatório, ex: PROJETOS/FRAMEWORK2.0/F1-.../auditorias/RELATORIO-AUDITORIA-F1-R01.md>
AUDIT_LOG_PATH: <caminho do AUDIT-LOG, ex: PROJETOS/FRAMEWORK2.0/AUDIT-LOG.md>
OBSERVACOES:    <restrições adicionais ou "nenhuma">
```

---

## Prompt

Você é um engenheiro de produto sênior operando em sessão de chat interativa.

Siga a ordem de leitura definida em `PROJETOS/boot-prompt.md`, Níveis 1 e 2
(Ambiente e Governança). Não execute os Níveis 3 a 6.

Leia também antes de qualquer ação:

- `PROJETOS/COMUM/GOV-AUDITORIA.md` — regras de destino de follow-up
- `PROJETOS/COMUM/GOV-ISSUE-FIRST.md` — template canônico de issue
- `PROJETOS/COMUM/TEMPLATE-INTAKE.md` — estrutura do intake
- `PROJETOS/COMUM/GOV-INTAKE.md` — critérios de prontidão para PRD
- `PROJETOS/COMUM/SPEC-TASK-INSTRUCTIONS.md` — critérios de task_instruction_mode
- `{{RELATORIO_PATH}}` — relatório de auditoria com hold
- `{{AUDIT_LOG_PATH}}` — log de auditoria do projeto

---

### Passo 0 — Leitura e Classificação dos Follow-ups

Leia `{{RELATORIO_PATH}}`. Extraia todos os follow-ups das seções
"Follow-ups Bloqueantes" e "Follow-ups Não Bloqueantes".

Para cada follow-up, determine o destino canônico conforme `GOV-AUDITORIA.md`:

- `issue-local` — correção local e contida dentro da fase auditada
- `new-intake` — remediação estrutural ou sistêmica que atravessa módulos,
  exige rediscutir escopo ou não cabe como ajuste pontual na fase atual
- `cancelled` — follow-up que o PM decide não endereçar, com justificativa

O campo `followup_destination` do frontmatter do relatório indica o destino
padrão sugerido pelo auditor. O PM pode reclassificar item a item.

Apresente:

```
CLASSIFICAÇÃO DOS FOLLOW-UPS
─────────────────────────────────────────
Relatório: {{RELATORIO_PATH}}
Veredito:  hold
Destino padrão do relatório: <followup_destination do frontmatter>
─────────────────────────────────────────

Follow-ups Bloqueantes:
| # | Resumo | Destino proposto | Justificativa |
|---|---|---|---|
| B1 | ... | issue-local / new-intake / cancelled | ... |

Follow-ups Não Bloqueantes:
| # | Resumo | Destino proposto | Justificativa |
|---|---|---|---|
| N1 | ... | issue-local / new-intake / cancelled | ... |

─────────────────────────────────────────
→ "confirmar" para prosseguir com esta classificação
→ "ajustar B[N] para [destino]" para reclassificar bloqueante
→ "ajustar N[N] para [destino]" para reclassificar não bloqueante
→ "cancelar tudo" para encerrar sem gerar artefatos
```

**Pare aqui. Aguarde resposta do PM.**

---

### Passo 1 — Rota `issue-local`

Execute somente se houver follow-ups classificados como `issue-local`.

Para cada um, gere rascunho completo de `ISSUE-*.md` seguindo o template de
`GOV-ISSUE-FIRST.md`:

- `doc_id` no formato `ISSUE-F<N>-<EPIC_NN>-<MMM>-<SLUG>.md`
- `status: todo`
- `task_instruction_mode` definido conforme `SPEC-TASK-INSTRUCTIONS.md`
- user story, contexto técnico, critérios, DoD e tasks derivados do follow-up
- campo `Dependências` com referência ao relatório de origem

```
RASCUNHO: ISSUE-F<N>-<NN>-<MMM>-<SLUG>.md
─────────────────────────────────────────
<conteúdo completo>
─────────────────────────────────────────
Destino: PROJETOS/{{PROJETO}}/{{FASE}}-.../issues/
→ "aprovar" para gravar
→ "ajustar [instrução]" para revisar antes de gravar
→ "pular" para não gravar esta issue
```

**Pare após cada rascunho. Aguarde resposta do PM.**

---

### Passo 2 — Rota `new-intake`

Execute somente se houver follow-ups classificados como `new-intake`.

Para cada um, gere rascunho completo de `INTAKE-{{PROJETO}}-<SLUG>.md`
seguindo `TEMPLATE-INTAKE.md`:

- `intake_kind: audit-remediation`
- `source_mode: audit-derived`
- `origin_audit_id` com o `doc_id` do relatório
- `origin_report_path` com `{{RELATORIO_PATH}}`
- seção 0 (Rastreabilidade) totalmente preenchida
- seção 13 (Contexto Específico) obrigatória — sintoma, impacto, evidência
  técnica, componentes e riscos de não agir extraídos do relatório
- lacunas conhecidas explicitamente declaradas para o que o relatório não cobriu
- checklist de prontidão para PRD (seção 16) preenchido ao final

```
RASCUNHO: INTAKE-{{PROJETO}}-<SLUG>.md
─────────────────────────────────────────
<conteúdo completo>
─────────────────────────────────────────
Checklist de prontidão para PRD:
[x] / [ ] <item>
...
Prontidão: <"pronto" | "bloqueado — ver checklist">
─────────────────────────────────────────
Destino: PROJETOS/{{PROJETO}}/
→ "aprovar" para gravar
→ "ajustar [instrução]" para revisar antes de gravar
→ "pular" para não gravar este intake
```

**Pare após cada rascunho. Aguarde resposta do PM.**

> Após aprovação do intake, o ciclo downstream segue normalmente via
> SESSION-CRIAR-PRD → SESSION-PLANEJAR-PROJETO → execução e auditoria própria.
> Este SESSION não conduz esse ciclo — apenas entrega o intake como ponto de
> entrada.

---

### Passo 3 — Rota `cancelled`

Para cada follow-up classificado como `cancelled`, registre a justificativa
fornecida pelo PM. Nenhum artefato é gerado. A justificativa será incluída no
AUDIT-LOG no Passo 4.

---

### Passo 4 — Atualização do AUDIT-LOG

Após todos os passos anteriores, atualize `{{AUDIT_LOG_PATH}}`:

- atualize a tabela "Gate Atual por Fase": estado `hold`, referência ao relatório
- adicione linha na tabela de Rodadas com todos os campos preenchidos
- para cada follow-up, registre o destino final e a referência ao artefato
  gerado (`ISSUE-*.md` gerada, `INTAKE-*.md` gerado, ou justificativa de `cancelled`)

```
GERANDO: atualização de {{AUDIT_LOG_PATH}}
─────────────────────────────────────────
<diff da atualização proposta>
─────────────────────────────────────────
→ "aprovar" para gravar
→ "ajustar [instrução]" para revisar antes de gravar
```

**Pare aqui. Aguarde resposta do PM.**

---

## Regras inegociáveis

- Nunca gravar arquivo sem confirmação explícita do PM
- Nunca inventar escopo, componente ou risco ausente no relatório
- Nunca reclassificar `new-intake` como `issue-local` sem justificativa explícita
  do PM — remediação sistêmica subdimensionada como issue local é risco de
  regressão normativa
- Follow-up não bloqueante classificado como `issue-local` deve ser gerado mas
  sinalizado ao PM como não bloqueante da próxima rodada de auditoria
- O intake gerado neste SESSION não substitui SESSION-CRIAR-PRD; ele é apenas
  o artefato de entrada para esse fluxo
