---
doc_id: "SESSION-AUDITAR-FASE.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-09"
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
os epicos e issues da fase, o ultimo relatorio da fase e use:

- `PROJETOS/COMUM/PROMPT-AUDITORIA.md`
- `PROJETOS/COMUM/TEMPLATE-AUDITORIA-RELATORIO.md`
- `PROJETOS/COMUM/SPEC-ANTI-MONOLITO.md`

### Passo 0 - Escopo auditado

Apresente fontes de evidencia e riscos de contexto antes de qualquer veredito.

### Passo 1 - Achados preliminares

Apresente os achados em categorias. Em caso de monolito acima de threshold, ofereca:

```text
MONOLITO DETECTADO: <arquivo ou funcao>
→ "gerar intake" para acionar `PROMPT-MONOLITO-PARA-INTAKE.md`
→ "seguir auditoria" para manter o achado no relatorio
```

### Passo 2 - Veredito proposto

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

### Passo 3 - Gravacao

Antes de gravar cada artefato, anuncie:

```text
GERANDO: <arquivo>
→ "sim" / "pular" / "ajustar [instrucao]"
```

Sem confirmacao explicita do PM, a sessao deve parar antes de qualquer gravacao.
