---
doc_id: "TASK-1.md"
user_story_id: "US-6-05-CONVIVENCIA-SOLICITACAO-LEGADO"
task_id: "T1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on: []
parallel_safe: false
write_scope:
  - "docs/adr/ATIVOS-INGRESSOS-feature6-convivencia-solicitacao-ingresso.md"
tdd_aplicavel: false
---

# TASK-1 - Local, nome e esqueleto do ADR de convivencia FEATURE-6 x SolicitacaoIngresso

## objetivo

Fixar o caminho e o nome do documento de convivencia entre o fluxo novo de
FEATURE-6 (distribuicao, remanejamento, ajustes, problemas) e o modelo legado
`SolicitacaoIngresso` / cotas agregadas; criar o ficheiro com esqueleto de
seccoes alinhadas aos criterios Given/When/Then da US-6-05 e ao PRD sec. **4.0**
e **2.6**, sem ainda redigir a matriz operacional completa (isso e T2).

## precondicoes

- `README.md` da US-6-05 lido (criterios de aceite, dependencias US-6-01..04,
  artefato minimo).
- Acesso ao repositorio para criar `docs/adr/` se ainda nao existir.
- Se outro ADR de coexistencia geral existir ou for criado pela US-2-01, confirmar
  que este ficheiro e **addendum** a coexistencia geral (referencia cruzada), nao
  duplicado do baseline inteiro.

## orquestracao

- `depends_on`: nenhuma (`[]`).
- `parallel_safe`: `false` (define ficheiro canónico tocado por T2 e referenciado
  em T4).
- `write_scope`: novo ADR em `docs/adr/`; nenhum codigo de aplicacao.

## arquivos_a_ler_ou_tocar

- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-6-DISTRIBUICAO-REMANEJAMENTO-AJUSTES-PROBLEMAS/user-stories/US-6-05-CONVIVENCIA-SOLICITACAO-LEGADO/README.md`
- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-6-DISTRIBUICAO-REMANEJAMENTO-AJUSTES-PROBLEMAS/FEATURE-6.md`
- `PROJETOS/ATIVOS-INGRESSOS/PRD-ATIVOS-INGRESSOS.md` (sec. 2.6, 4.0, 4.1, 8 — rollout)
- `docs/adr/ATIVOS-INGRESSOS-coexistencia-legado-e-novo-dominio.md` *(se existir;
  citar como documento pai de coexistencia)*
- `docs/adr/ATIVOS-INGRESSOS-feature6-convivencia-solicitacao-ingresso.md` *(criar)*

## testes_red

> Nao aplicavel (`tdd_aplicavel: false`).

## passos_atomicos

1. Confirmar o caminho canónico:
   `docs/adr/ATIVOS-INGRESSOS-feature6-convivencia-solicitacao-ingresso.md`
   (ajustar apenas se o gate fixar outro nome, mantendo convencao `docs/adr/`).
2. Criar o directório `docs/adr/` no root do monolito se nao existir.
3. Criar o ficheiro com frontmatter ou cabecalho minimo (titulo, status `proposed`,
   data, ligacao a `US-6-05` e `FEATURE-6`) e seccoes placeholder para: (a)
   contexto e baseline (PRD 4.0 / 2.6); (b) relacao com ADR de coexistencia geral
   (US-2-01) se aplicavel; (c) matriz **operacao nova vs legado** *(corpo em T2)*;
   (d) dados que nao se misturam sem migracao *(corpo em T2)*; (e) mapeamento
   `SolicitacaoIngresso` / estados e fluxos FEATURE-6 *(corpo em T2)*; (f)
   cenarios de teste e validacao *(referencias finais em T3–T4)*; (g) referencias
   e rastreabilidade.
4. Na introducao, citar explicitamente `PRD-ATIVOS-INGRESSOS.md` sec. **4.0** e
   **2.6** (sem copiar o PRD como backlog).
5. Listar em "Referencias" os caminhos das leituras obrigatorias acima e os
   modulos legados indicados na US (`models.py`, `ingressos.py`, testes de rotas).

## comandos_permitidos

- `ls`, `mkdir` *(apenas para `docs/adr/` se necessario)*
- `rg` / `grep` *(confirmar ausencia de ficheiro homónimo ou conflito de nome)*

## resultado_esperado

Existe `docs/adr/ATIVOS-INGRESSOS-feature6-convivencia-solicitacao-ingresso.md`
com esqueleto utilizavel; mencao explicita ao PRD 4.0 e 2.6; corpo detalhado da
matriz e invariantes fica para T2.

## testes_ou_validacoes_obrigatorias

- Abrir o ficheiro e confirmar que as areas (contexto, relacao coexistencia geral,
  placeholders para matriz, dados, mapeamento estados, testes, referencias) estao
  como seccoes.
- Confirmar mencao explicita a PRD sec. 4.0 e 2.6 na introducao ou contexto.

## stop_conditions

- Parar e escalar se ja existir outro documento aprovado com o mesmo objectivo
  (convivencia FEATURE-6 x `SolicitacaoIngresso`); alinhar fusao ou nome com o
  agente senior antes de continuar.
