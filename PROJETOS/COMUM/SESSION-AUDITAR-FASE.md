---
doc_id: "SESSION-AUDITAR-FASE.md"
version: "1.4"
status: "active"
owner: "PM"
last_updated: "2026-03-16"
---

# SESSION-AUDITAR-FASE - Auditoria de Fase em Sessao de Chat

## Parametros obrigatorios

```
PROJETO:       <nome do projeto>
FASE:          <F<N>-NOME>
RODADA:        <R<NN>>
BASE_COMMIT:   <sha ou "worktree">
AUDIT_LOG:     <caminho completo do AUDIT-LOG.md>
```

## Prompt

Voce e um engenheiro senior operando em sessao de chat interativa.

Siga `PROJETOS/boot-prompt.md`, Niveis 1, 2 e 3. Depois leia o manifesto da fase,
os epicos e issues da fase (para issue granularizada, ler `README.md` e
`TASK-*.md`; para issue legada, ler `ISSUE-*.md`), o ultimo relatorio da fase e use:

- `PROJETOS/COMUM/PROMPT-AUDITORIA.md`
- `PROJETOS/COMUM/TEMPLATE-AUDITORIA-RELATORIO.md`
- `PROJETOS/COMUM/SPEC-ANTI-MONOLITO.md`

### Passo 0 - Pre-checagem de elegibilidade

Antes de qualquer leitura de escopo, verifique se a fase está apta para nova
rodada.

Leia o `AUDIT-LOG.md` do projeto. Localize a entrada mais recente da fase na
tabela de Rodadas e verifique seu veredito:

- se o veredito da rodada mais recente for `go` ou se não houver rodada anterior,
  a fase é elegível — prossiga para o Passo 1
- se o veredito da rodada mais recente for `hold`, execute a verificação abaixo

**Verificação de follow-ups da rodada hold imediatamente anterior**

Identifique o `Audit ID` da rodada `hold` mais recente. Na seção
`Resolucoes de Follow-ups`, considere apenas as linhas em que:

- `Audit ID de Origem` = `Audit ID` da rodada `hold` mais recente
- `Fase` = fase auditada

Se a seção `Resolucoes de Follow-ups` não existir, se a coluna
`Audit ID de Origem` estiver ausente ou se não houver rastreabilidade
suficiente para identificar os follow-ups da rodada `hold` imediatamente
anterior, responda `BLOQUEADO` e pare sem gerar relatório.

Para cada follow-up dessa rodada, determine a situação pelo tipo:

| Tipo | Como verificar | Elegível para encerrar? |
|---|---|---|
| `ISSUE-*` | ler o `status` no frontmatter do arquivo ou do `README.md` da pasta | `done` ou `cancelled` |
| `INTAKE-*.md` | verificar se o arquivo existe e tem intake_kind registrado | sempre elegível — intake aberto não bloqueia nova rodada |
| `cancelled` (sem arquivo) | a linha no log já registra o destino como `cancelled` | sempre elegível |

Apresente:

```text
PRE-CHECAGEM DE ELEGIBILIDADE
─────────────────────────────────────────
Rodada hold de referência: <Audit ID>
Gate atual da fase:        <hold>

Follow-ups bloqueantes dessa rodada:
| Ref | Tipo | Destino | Status atual | Elegível? |
|---|---|---|---|---|
| ISSUE-* | bloqueante | issue-local | todo/active/done/cancelled | sim/nao |

Follow-ups nao bloqueantes dessa rodada:
| Ref | Tipo | Destino | Status atual |
|---|---|---|---|
| INTAKE-*.md | nao bloqueante | new-intake | criado |
| — | nao bloqueante | cancelled | registrado no log |

Resultado: <ELEGÍVEL | BLOQUEADO>
─────────────────────────────────────────
```

**Regra de elegibilidade:** a nova rodada só pode prosseguir se todas as
`ISSUE-*` de follow-ups **bloqueantes** da rodada hold imediatamente anterior
estiverem `done` ou `cancelled`. `INTAKE-*.md` e entradas `cancelled` nunca
bloqueiam nova rodada.

Follow-ups de rodadas anteriores mais antigas e follow-ups de outras fases
não entram nesta verificação.

Se o resultado for `BLOQUEADO`:

```text
BLOQUEADO — issues de follow-up bloqueantes ainda abertas:
- <ISSUE-*> (status: todo/active)
...
A nova rodada não pode iniciar até que essas issues sejam encerradas.
→ Use SESSION-IMPLEMENTAR-ISSUE.md para cada issue pendente.
```

Encerre a sessão sem produzir relatório, sem atualizar o log e sem mudar o gate.

Se o resultado for `ELEGÍVEL`, prossiga para o Passo 1.

---

### Passo 1 - Escopo auditado

Apresente fontes de evidencia e riscos de contexto antes de qualquer veredito.

### Passo 2 - Achados preliminares

Apresente os achados em categorias. Em caso de monolito acima de threshold, ofereca:

```text
MONOLITO DETECTADO: <arquivo ou funcao>
→ "gerar intake" para acionar `PROMPT-MONOLITO-PARA-INTAKE.md`
→ "seguir auditoria" para manter o achado no relatorio
```

### Passo 3 - Veredito proposto

Apresente:

```text
VEREDITO PROPOSTO
─────────────────────────────────────────
veredito:
gate_da_fase:
follow-ups bloqueantes:
follow-up padrao:
─────────────────────────────────────────
→ "aprovar" para gerar relatorio e atualizar log
→ "ajustar [instrucao]" para revisar
```

Nao grave relatorio, audit log ou intake de follow-up neste passo.

### Passo 4 - Gravacao

Antes de gravar cada artefato, anuncie:

```text
GERANDO: <arquivo>
→ "sim" / "pular" / "ajustar [instrucao]"
```

Sem confirmacao explicita do PM, a sessao deve parar antes de qualquer gravacao.

### Passo 5 - Pós-Hold

Execute somente se o veredito for `hold`.

Após gravar o relatório e atualizar o AUDIT-LOG, informe o PM:

```text
AUDITORIA CONCLUÍDA — VEREDITO: hold
─────────────────────────────────────────
Follow-ups bloqueantes: <N>
Follow-ups não bloqueantes: <N>
─────────────────────────────────────────
Próximo passo: use SESSION-REMEDIAR-HOLD.md para converter os
follow-ups nos artefatos corretos (issue-local, new-intake ou cancelled).

RELATORIO_PATH: <caminho do relatório recém-gravado>
AUDIT_LOG_PATH: <caminho do AUDIT-LOG>
─────────────────────────────────────────
Cole SESSION-REMEDIAR-HOLD.md em uma nova sessão com os parâmetros acima.
```

Esta sessão encerra aqui. O roteamento de remediação ocorre em sessão separada.
