---
doc_id: "TASK-4.md"
user_story_id: "US-2-01-ADR-E-COEXISTENCIA"
task_id: "T4"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T3"
parallel_safe: false
write_scope:
  - "docs/adr/ATIVOS-INGRESSOS-coexistencia-legado-e-novo-dominio.md"
tdd_aplicavel: false
---

# TASK-4 - Rastreabilidade, referencias cruzadas e checklist de aceite

## objetivo

Fechar o ADR com ligacoes claras ao `PRD-ATIVOS-INGRESSOS.md` sec. **4.0** e,
quando util, aos anexos citados no manifesto FEATURE-2; validar o documento
contra todos os Given/When/Then da US-2-01. **Nao** alterar
`FEATURE-2.md` nesta task salvo instrucao explicita do gate (default: apenas
ADR).

## precondicoes

- T3 concluida: transicao e rollout redigidos no ADR.
- README da US com lista de tasks actualizada.

## orquestracao

- `depends_on`: `["T3"]`.
- `parallel_safe`: `false`.
- `write_scope`: ficheiro ADR apenas (validacao documental).

## arquivos_a_ler_ou_tocar

- `docs/adr/ATIVOS-INGRESSOS-coexistencia-legado-e-novo-dominio.md`
- `PROJETOS/ATIVOS-INGRESSOS/PRD-ATIVOS-INGRESSOS.md` (4.0, 8)
- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-2-DOMINIO-COEXISTENCIA-E-ROLOUT/FEATURE-2.md`
- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-2-DOMINIO-COEXISTENCIA-E-ROLOUT/user-stories/US-2-01-ADR-E-COEXISTENCIA/README.md`
- `backend/docs/auditoria_eventos/ATIVOS_STATE_NOW.md`
- `docs/auditoria_eventos/RESTORE_ATIVOS_SUMMARY.md`

## testes_red

> Nao aplicavel (`tdd_aplicavel: false`).

## passos_atomicos

1. Na seccao "Referencias" ou "Rastreabilidade", incluir links relativos do repo
   para: PRD (ficheiro e ancoragem conceptual a sec. 4.0); FEATURE-2.md;
   `ATIVOS_STATE_NOW.md`; `RESTORE_ATIVOS_SUMMARY.md` quando suportarem
   decisoes do ADR.
2. Adicionar uma subseccao "Checklist de aceite (US-2-01)" mapeando cada
   Given/When/Then da US a uma frase ou paragrafo concreto do ADR (ou indicar
   seccao).
3. Revisar ortografia, consistencia de termos (`CotaCortesia`,
   `SolicitacaoIngresso`, rollout, evento) e remover placeholders vazios
   deixados em T1.
4. Actualizar o estado do ADR no frontmatter (ex.: `accepted` ou `proposed`)
   conforme processo do projeto; se o processo exigir revisao formal, deixar
   `proposed` ate aprovacao humana.
5. Nao editar o manifesto FEATURE-2 nem o PRD nesta task.

## comandos_permitidos

- `rg` / `grep` *(verificar que strings-chave PRD 4.0 / sec. 8 aparecem no ADR)*

## resultado_esperado

ADR completo, rastreavel e alinhado aos criterios da US-2-01; pronto para
revisao pos-US ou auditoria conforme fluxo do projeto.

## testes_ou_validacoes_obrigatorias

- Checklist US-2-01: tres blocos Given/When/Then cobertos com referencia a
  seccoes do ADR.
- Confirmar link ou citacao explicita a `PRD-ATIVOS-INGRESSOS.md` sec. 4.0.
- Ler o ADR de principio a fim como revisao final.

## stop_conditions

- Parar se faltar conteudo obrigatorio das T2/T3; reabrir task anterior em vez
  de marcar T4 como concluida.
