---
doc_id: "F2_LP-PREVIEW_EPICS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
audit_gate: "not_ready"
---

# Epicos - LP-PREVIEW / F2 - Implementacao

## Objetivo da Fase

Implementar layout side-by-side (painel esquerdo + preview direito), preview fixo e visivel durante toda a sessao, frame visual de celular com viewport ~390px, e tratamento de breakpoint para viewports menores.

## Gate de Saida da Fase

- Preview visivel ao lado do painel durante toda a sessao
- Preview renderiza em viewport mobile com frame de celular
- Reatividade preservada em ambos os contextos
- Layout colapsa adequadamente em viewports menores

## Estado do Gate de Auditoria

- gate_atual: `not_ready`
- ultima_auditoria: `nao_aplicavel`

## Checklist de Transicao de Gate

> A semântica dos vereditos e as regras de julgamento vivem em `GOV-AUDITORIA.md`.

### `not_ready -> pending`
- [ ] todos os epicos estao `done`
- [ ] todas as issues filhas estao `done`
- [ ] DoD da fase foi revisado

### `pending -> hold`
- [ ] existe `RELATORIO-AUDITORIA-F2-R<NN>.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `hold`
- [ ] o estado do gate foi atualizado para `hold`

### `pending -> approved`
- [ ] existe `RELATORIO-AUDITORIA-F2-R<NN>.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `go`
- [ ] o estado do gate foi atualizado para `approved`

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F2-01 | Layout Side-by-Side | Converter para duas colunas e reposicionar preview fixo a direita | F1 done | todo | [EPIC-F2-01-Layout-Side-by-Side.md](./EPIC-F2-01-Layout-Side-by-Side.md) |
| EPIC-F2-02 | Frame Mobile e Breakpoints | Frame celular 390px e tratamento de viewports menores | EPIC-F2-01 | todo | [EPIC-F2-02-Frame-Mobile-Breakpoints.md](./EPIC-F2-02-Frame-Mobile-Breakpoints.md) |

## Dependencias entre Epicos

- `EPIC-F2-01`: depende de F1 (Discovery) concluida
- `EPIC-F2-02`: depende de EPIC-F2-01 (layout base pronto para receber frame)

## Escopo desta Fase

### Dentro
- Conversao de layout para duas colunas (painel + preview)
- Preview fixo a direita, visivel durante toda a sessao
- Frame visual de celular com viewport ~390px
- Tratamento de breakpoint para viewports menores
- Compatibilidade com ambos os contextos (leads e landing page)
- Manutencao da reatividade existente

### Fora
- Alterar logica de configuracao dos formularios
- Zoom, troca de dispositivo, modo desktop no preview
- Nova dependencia de biblioteca externa sem aprovacao

## Definition of Done da Fase
- [ ] Layout side-by-side implementado
- [ ] Preview fixo e visivel durante toda a sessao
- [ ] Frame mobile 390px aplicado
- [ ] Breakpoint e colapso em viewports menores funcionando
- [ ] Reatividade preservada
- [ ] Auditoria F2 aprovada com veredito `go`
