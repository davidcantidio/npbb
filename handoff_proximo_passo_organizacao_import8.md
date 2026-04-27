# Handoff 8 - proximo agente para implementacao da proxima rodada de importacao

## Contexto resumido

A `FEATURE-9` ja foi implementada como **rodada documental**. O repositorio
agora tem governanca explicita registrando que:

- o shell canonico de `/leads/importar` continua em
  `frontend/src/pages/leads/ImportacaoPage.tsx`;
- `frontend/src/pages/leads/importacao/**`,
  `MapeamentoPage.tsx`, `BatchMapeamentoPage.tsx` e
  `PipelineStatusPage.tsx` continuam acoplados ao shell atual;
- nenhuma migracao funcional foi feita nesta rodada;
- qualquer migracao futura para `frontend/src/features/leads/importacao`
  depende de **feature posterior propria**;
- backend, ETL, Bronze, pipeline, contratos HTTP e rotas publicas seguem fora
  do escopo.

Em outras palavras: a decisao/preparacao foi concluida. O proximo agente nao
precisa reabrir a discussao da `FEATURE-9`; ele precisa usar essa base para
**implementar a proxima feature**, se for autorizada.

## O que foi implementado agora

Foram criados e atualizados os seguintes artefatos:

- `PROJETOS/NPBB/INTAKE-DECISAO-SHELL-IMPORTACAO-LEADS.md`
- `PROJETOS/NPBB/PRD-DECISAO-SHELL-IMPORTACAO-LEADS.md`
- `PROJETOS/NPBB/features/FEATURE-9-DECISAO-SHELL-IMPORTACAO-LEADS/FEATURE-9-DECISAO-SHELL-IMPORTACAO-LEADS.md`
- `PROJETOS/NPBB/features/FEATURE-9-DECISAO-SHELL-IMPORTACAO-LEADS/user-stories/US-9-01-DECIDIR-SHELL-IMPORTACAO-LEADS/README.md`
- `PROJETOS/NPBB/features/FEATURE-9-DECISAO-SHELL-IMPORTACAO-LEADS/user-stories/US-9-01-DECIDIR-SHELL-IMPORTACAO-LEADS/TASK-1.md`
- `plano_organizacao_import.md`

A rodada registrou o inventario e a decisao, mas **nao** moveu:

- `frontend/src/pages/leads/ImportacaoPage.tsx`
- `frontend/src/pages/leads/importacao/**`
- `frontend/src/pages/leads/MapeamentoPage.tsx`
- `frontend/src/pages/leads/BatchMapeamentoPage.tsx`
- `frontend/src/pages/leads/PipelineStatusPage.tsx`

## Leitura obrigatoria para o proximo agente

Ler nesta ordem:

1. `plano_organizacao_import.md`
2. `handoff_proximo_passo_organizacao_import8.md`
3. `PROJETOS/NPBB/PRD-DECISAO-SHELL-IMPORTACAO-LEADS.md`
4. `PROJETOS/NPBB/features/FEATURE-9-DECISAO-SHELL-IMPORTACAO-LEADS/FEATURE-9-DECISAO-SHELL-IMPORTACAO-LEADS.md`
5. `PROJETOS/NPBB/features/FEATURE-9-DECISAO-SHELL-IMPORTACAO-LEADS/user-stories/US-9-01-DECIDIR-SHELL-IMPORTACAO-LEADS/README.md`

Depois, para entender o codigo real antes de propor implementacao:

6. `frontend/src/app/AppRoutes.tsx`
7. `frontend/src/pages/leads/ImportacaoPage.tsx`
8. `frontend/src/pages/leads/importacao/ImportacaoUploadStep.tsx`
9. `frontend/src/pages/leads/importacao/useLeadImportEtlJobPolling.ts`
10. `frontend/src/pages/leads/importacao/batch/useBatchUploadDraft.ts`
11. `frontend/src/pages/leads/MapeamentoPage.tsx`
12. `frontend/src/pages/leads/BatchMapeamentoPage.tsx`
13. `frontend/src/pages/leads/PipelineStatusPage.tsx`

Se a proxima rodada for realmente de migracao parcial, ler tambem:

14. `frontend/src/pages/__tests__/ImportacaoPage.test.tsx`
15. `frontend/src/pages/__tests__/MapeamentoPage.test.tsx`
16. `frontend/src/pages/__tests__/BatchMapeamentoPage.test.tsx`
17. `frontend/src/pages/__tests__/PipelineStatusPage.test.tsx`
18. `frontend/src/features/leads/index.ts`
19. `frontend/src/features/leads/list/LeadsListPage.tsx`
20. `frontend/src/features/leads/dashboard/LeadsAgeAnalysisPage.tsx`

## Leitura opcional, mas util para contexto historico

- `handoff_proximo_passo_organizacao_import7.md`
- `PROJETOS/NPBB/PRD-REMOCAO-WRAPPERS-FRONTEND-LEADS.md`
- `PROJETOS/NPBB/features/FEATURE-8-REMOCAO-WRAPPERS-FRONTEND-LEADS/FEATURE-8-REMOCAO-WRAPPERS-FRONTEND-LEADS.md`

## Estado atual confirmado

- `/leads` e `/dashboard/leads/analise-etaria` ja usam `frontend/src/features/leads`.
- `/leads/importar` ainda lazy-loada `../pages/leads/ImportacaoPage`.
- `ImportacaoPage.tsx` ainda importa:
  - `./BatchMapeamentoPage`
  - `./MapeamentoPage`
  - `./PipelineStatusPage`
- testes de importacao/mapeamento/pipeline ainda importam de
  `frontend/src/pages/leads`.
- `app.modules.lead_imports` e o unico caminho backend real.
- `app.modules.leads_publicidade` nao deve ser recriado.

## O que o proximo agente deve assumir

- A `FEATURE-9` esta concluida e nao precisa ser refeita.
- O proximo trabalho, se autorizado, sera uma **feature de implementacao**,
  nao outra rodada documental.
- O caminho preferencial futuro e avaliar migracao parcial para
  `frontend/src/features/leads/importacao`.
- Essa migracao parcial nao pode inventar mudanca funcional em ETL, Bronze,
  mapeamento, pipeline ou backend.

## O que o proximo agente nao deve assumir

- Nao assumir que todo o shell pode ser movido de uma vez.
- Nao assumir que `ImportacaoPage.test.tsx` esta pronta para entrar no gate
  principal sem revisao.
- Nao assumir que `MapeamentoPage`, `BatchMapeamentoPage` e
  `PipelineStatusPage` pertencem automaticamente ao mesmo slice novo.
- Nao assumir que sera preciso mexer em backend para reorganizar frontend.
- Nao assumir qualquer reabertura de `/dashboard/leads/conversao`.

## Proximo passo recomendado

Se o objetivo for sair da decisao e entrar em implementacao, o proximo passo
coerente e abrir uma feature nova de implementacao, com escopo pequeno:

1. decidir quais componentes de `frontend/src/pages/leads/importacao/**` sao
   realmente puros e moviveis;
2. mover primeiro apenas componentes/helpers/hooks de UI sem arrastar
   `MapeamentoPage`, `BatchMapeamentoPage` e `PipelineStatusPage`;
3. manter `ImportacaoPage.tsx` como borda temporaria se isso reduzir risco;
4. ajustar imports internos e testes focados conforme os arquivos realmente
   movidos;
5. preservar `/leads/importar` sem alteracao de comportamento.

## Guardrails obrigatorios

- Nao tocar em `lead_pipeline/`.
- Nao tocar em `core/leads_etl/`.
- Nao alterar backend, schemas, contratos HTTP ou rotas publicas.
- Nao recriar wrappers removidos em `FEATURE-8`.
- Nao recriar `app.modules.leads_publicidade`.
- Nao transformar a rodada em refactor total do shell.
- Preservar mudancas locais nao relacionadas ja existentes no worktree.

## Validacoes minimas para a proxima sessao

Antes de editar:

- `git status --short`
- `git log -1 --oneline`
- `rg -n "ImportacaoPage|pages/leads/importacao|PipelineStatusPage|MapeamentoPage|BatchMapeamentoPage" frontend/src`
- `rg -n "app\\.modules\\.leads_publicidade|leads_publicidade" backend/app backend/scripts backend/tests`

Se houver mudanca em frontend:

- `cd frontend && npm run typecheck`
- rodar apenas os testes focados dos arquivos realmente tocados

Se aparecer necessidade de tocar backend/importacao funcional:

- parar e abrir nova feature com gate proprio

## Checklist para o proximo agente

- [ ] Ler os arquivos da secao "Leitura obrigatoria para o proximo agente".
- [ ] Confirmar baseline com `git status --short` e `git log -1 --oneline`.
- [ ] Confirmar que `/leads/importar` ainda aponta para `ImportacaoPage.tsx`.
- [ ] Confirmar que `app.modules.leads_publicidade` segue ausente.
- [ ] Separar o que e componente puro de UI do que e fluxo funcional acoplado.
- [ ] Propor ou abrir feature de implementacao antes de mover arquivos.
- [ ] Nao mover `MapeamentoPage`, `BatchMapeamentoPage` ou `PipelineStatusPage`
      sem justificativa explicita e gate proprio.
- [ ] Registrar validacoes executadas no plano/handoff seguinte.
