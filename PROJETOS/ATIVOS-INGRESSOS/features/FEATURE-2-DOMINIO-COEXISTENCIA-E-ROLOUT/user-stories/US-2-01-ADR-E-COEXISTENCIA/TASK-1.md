---
doc_id: "TASK-1.md"
user_story_id: "US-2-01-ADR-E-COEXISTENCIA"
task_id: "T1"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-27"
depends_on: []
parallel_safe: false
write_scope:
  - "docs/adr/ATIVOS-INGRESSOS-coexistencia-legado-e-novo-dominio.md"
tdd_aplicavel: false
---

# TASK-1 - Local, nome e esqueleto do ADR de coexistencia

## objetivo

Fixar o caminho e o nome versionado do ADR (ou documento de convivencia), criar
o ficheiro com esqueleto de seccoes alinhadas aos criterios Given/When/Then da
US-2-01, e deixar explicitas as leituras obrigatorias antes de redigir o corpo
nas tasks seguintes.

## precondicoes

- `README.md` da US-2-01 lido (criterios de aceite e artefato minimo).
- Acesso ao repositorio para criar `docs/adr/` se ainda nao existir.

## orquestracao

- `depends_on`: nenhuma (`[]`).
- `parallel_safe`: `false` (define ficheiro canónico tocado por T2–T4).
- `write_scope`: novo ADR em `docs/adr/`; nenhum codigo de aplicacao.

## arquivos_a_ler_ou_tocar

- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-2-DOMINIO-COEXISTENCIA-E-ROLOUT/user-stories/US-2-01-ADR-E-COEXISTENCIA/README.md`
- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-2-DOMINIO-COEXISTENCIA-E-ROLOUT/FEATURE-2.md`
- `PROJETOS/ATIVOS-INGRESSOS/PRD-ATIVOS-INGRESSOS.md` (sec. 4.0, 4.1, 8)
- `backend/docs/auditoria_eventos/ATIVOS_STATE_NOW.md`
- `docs/auditoria_eventos/RESTORE_ATIVOS_SUMMARY.md`
- `docs/adr/ATIVOS-INGRESSOS-coexistencia-legado-e-novo-dominio.md` *(criar)*

## testes_red

> Nao aplicavel (`tdd_aplicavel: false`).

## passos_atomicos

1. Confirmar que o caminho canónico do ADR e
   `docs/adr/ATIVOS-INGRESSOS-coexistencia-legado-e-novo-dominio.md` (ajustar
   apenas se o gate do projeto fixar outro nome, mantendo convencao em
   `docs/adr/`).
2. Criar o directório `docs/adr/` no root do monolito se nao existir.
3. Criar o ficheiro do ADR com frontmatter minimo (titulo, status `proposed`,
   data, ligacao a `user_story_id` e `feature_key` FEATURE-2) e seccoes vazias
   ou com bullets placeholder para: (a) contexto e baseline; (b) modelo
   agregado legado vs novo dominio ate ao rollout; (c) estrategia de transicao
   (ex.: leitura dupla, gate por evento); (d) rastreabilidade e referencias.
4. Na introducao do ADR, citar explicitamente o baseline em
   `PRD-ATIVOS-INGRESSOS.md` sec. **4.0** (sem copiar o PRD como backlog).
5. Listar no ADR, em "Referencias", os caminhos das leituras obrigatorias acima.

## comandos_permitidos

- `ls`, `mkdir` *(apenas para `docs/adr/` se necessario)*
- `rg` / `grep` *(confirmar ausencia de ficheiro homónimo ou conflito de nome)*

## resultado_esperado

Existe `docs/adr/ATIVOS-INGRESSOS-coexistencia-legado-e-novo-dominio.md` com
esqueleto utilizavel e referencias ao PRD 4.0 e as fontes listadas; corpo
detalhado fica para T2–T4.

## testes_ou_validacoes_obrigatorias

- Abrir o ficheiro e confirmar que as quatro areas (baseline/contexto, legado
  vs novo, transicao, rastreabilidade) estao representadas como seccoes.
- Confirmar mencao explicita a `PRD-ATIVOS-INGRESSOS.md` sec. 4.0 na
  introducao ou na seccao de contexto.

## stop_conditions

- Parar e escalar se ja existir outro ADR ou documento de convivencia aprovado
  para o mesmo objectivo (evitar duplicacao); alinhar nome ou fusao com o
  agente senior antes de continuar.
