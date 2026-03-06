# EPIC-F4-02 — Coerência Normativa e Gate de Fase
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** AJUSTE-FINO-LANDING-PAGES-DINAMICAS | **fase:** F4 | **status:** ✅

---
## 1. Resumo do Épico
Validar consistência entre a implementação e o contrato definido no PRD, verificar
cobertura de testes cross-camada (backend + frontend), e consolidar toda a evidência
de entrega das fases F1–F4 em um documento de validação com decisão `promote | hold`.

**Resultado de Negócio Mensurável:** Decisão documentada e fundamentada sobre a
promoção da entrega para produção, com rastreabilidade completa do que foi entregue,
testado e validado.

## 2. Contexto Arquitetural
- PRD de referência: `PROJETOS/AJUSTE-FINO-LANDING-PAGES-DINAMICAS/PRD-LANDING-REDESIGN-ATIVACAO-v1.2.md`
- Critérios de aceite: PRD seção 09 (LPD-REDESIGN-01 a LPD-REDESIGN-05)
- Testes backend: `backend/tests/`
- Testes frontend: `frontend/src/` (ou diretório de testes do frontend)
- Artefato de evidência: `artifacts/phase-f4/aflpd-validation-summary.md`
- Governança: `PROJETOS/COMUM/SCRUM-GOV.md`, `PROJETOS/COMUM/DECISION-PROTOCOL.md`

## 3. Riscos e Armadilhas
- Divergência silenciosa entre implementação e PRD — cada critério de aceite deve ser verificado individualmente
- Testes podem passar localmente mas falhar em CI — validar em ambiente equivalente ao CI
- Evidência incompleta pode bloquear decisão — cada fase deve ter status explícito
- Gate `hold` requer lista de ações corretivas — não pode ser genérico

## 4. Definition of Done do Épico
- [x] Cada critério de aceite do PRD (LPD-REDESIGN-01 a LPD-REDESIGN-05) verificado com resultado ✅ ou ❌
- [x] Cobertura de testes: ao menos 1 teste e2e cobrindo fluxo formulário → gamificação
- [x] Testes de contrato de API verificados (request/response match schemas)
- [x] `artifacts/phase-f4/aflpd-validation-summary.md` gerado com status de cada épico F1–F4
- [x] Decisão `promote | hold` documentada com justificativa

---
## Issues

### AFLPD-F4-02-001 — Validar critérios de aceite do PRD
**tipo:** docs | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** nenhuma

**Descrição:**
Percorrer cada critério de aceite definido no PRD seção 09 (blocos LPD-REDESIGN-01 a
LPD-REDESIGN-05) e verificar se a implementação atende. Registrar resultado por item
com evidência (screenshot, output de teste ou referência a arquivo).

**Plano TDD:**
- **Red:** Listar todos os critérios de aceite em checklist verificável com coluna de status.
- **Green:** Verificar cada item com evidência concreta — marcar ✅ ou ❌.
- **Refactor:** Para itens ❌, registrar issue de correção com severidade e prioridade.

**Critérios de Aceitação:**
- Given bloco LPD-REDESIGN-01 (layout/visual), When cada item verificado, Then resultado documentado com evidência
- Given bloco LPD-REDESIGN-03 (gamificação), When cada item verificado, Then transições de estado e chamada API confirmadas
- Given todos os 5 blocos, When verificação completa, Then tabela de resultados com 100% dos items preenchidos

**Tarefas:**
- [ ] T1: Verificar LPD-REDESIGN-01 (6 itens) — formulário above fold, borderRadius, chips, overlay, hero, logo
- [ ] T2: Verificar LPD-REDESIGN-02 (3 itens) — título ativação, callout, CTA
- [ ] T3: Verificar LPD-REDESIGN-03 (7 itens) — bloco gamificação, botões, transições, API, feedback, reset
- [ ] T4: Verificar LPD-REDESIGN-04 (4 itens) — migration, ativacao_lead_id, endpoint, query
- [ ] T5: Verificar LPD-REDESIGN-05 (4 itens) — payload ativação, gamificações array, campos mantidos, testes

**Notas técnicas:**
Cada verificação deve ter evidência rastreável: link para teste que passa, screenshot
com timestamp, ou referência a arquivo de código. Itens que falham devem gerar issues
de correção antes de consolidar o gate.

---
### AFLPD-F4-02-002 — Validar cobertura de testes cross-camada
**tipo:** docs | **sp:** 2 | **prioridade:** alta | **status:** 🔲
**depende de:** AFLPD-F4-02-001

**Descrição:**
Verificar que existe cobertura de testes adequada para as mudanças das fases F1–F3:
ao menos 1 teste e2e cobrindo o fluxo completo (formulário → gamificação), testes de
contrato de API (schemas match), e testes unitários dos componentes novos.

**Plano TDD:**
- **Red:** Listar testes esperados por camada (backend: migration, endpoints, schemas; frontend: componentes, integração).
- **Green:** Executar suíte de testes e confirmar que todos passam. Identificar lacunas.
- **Refactor:** Se lacunas críticas identificadas, criar issues de correção.

**Critérios de Aceitação:**
- Given testes backend, When executados com `pytest -q`, Then testes dos endpoints de landing e gamificação passam
- Given testes frontend, When executados, Then testes do `GamificacaoBlock` e `LandingPageView` passam
- Given fluxo e2e, When executado, Then formulário → submit → gamificação → conclusão funciona sem erro

**Tarefas:**
- [ ] T1: Executar `cd backend && TESTING=true python -m pytest -q` e documentar resultado
- [ ] T2: Executar testes frontend e documentar resultado
- [ ] T3: Verificar existência de teste e2e do fluxo completo (se não existir, registrar como gap)
- [ ] T4: Listar testes que cobrem as mudanças — tabela com teste × funcionalidade coberta

**Notas técnicas:**
Os 3 testes pré-existentes com falha em `test_leads_import_etl_usecases.py` devem
ser ignorados — são falhas conhecidas (strict keyword argument mismatch) não
relacionadas a este projeto.

---
### AFLPD-F4-02-003 — Consolidar evidência e emitir decisão promote/hold
**tipo:** docs | **sp:** 2 | **prioridade:** alta | **status:** 🔲
**depende de:** AFLPD-F4-02-002

**Descrição:**
Gerar o documento `artifacts/phase-f4/validation-summary.md` consolidando: status
de cada épico (F1 a F4), resultado dos critérios de aceite, cobertura de testes,
issues abertas, e decisão fundamentada `promote` ou `hold`.

**Plano TDD:**
- **Red:** Definir template do documento com seções obrigatórias: resumo, status por épico, critérios, testes, decisão.
- **Green:** Preencher cada seção com dados reais coletados nos issues anteriores.
- **Refactor:** Revisar linguagem para clareza e objetividade — sem suavização de problemas.

**Critérios de Aceitação:**
- Given evidências coletadas nos AFLPD-F4-02-001 e AFLPD-F4-02-002, When consolidadas, Then `validation-summary.md` contém status de cada épico F1–F4
- Given critérios de aceite verificados, When consolidados, Then tabela com resultado ✅/❌ por item presente no documento
- Given documento completo, When revisado, Then decisão `promote` ou `hold` presente com justificativa de no mínimo 3 frases

**Tarefas:**
- [x] T1: Criar `artifacts/phase-f4/aflpd-validation-summary.md` com template estruturado
- [x] T2: Preencher seção "Status por Épico" com resultado de cada épico F1–F4
- [x] T3: Preencher seção "Critérios de Aceite" com tabela de resultados
- [x] T4: Preencher seção "Cobertura de Testes" com resultado da suíte
- [x] T5: Preencher seção "Issues Abertas" com lista de pendências (se houver)
- [x] T6: Redigir seção "Decisão" com `promote` ou `hold`, justificativa e ações necessárias

**Notas técnicas:**
O documento é a evidência formal para o PO tomar a decisão final de go/no-go. Deve
ser objetivo, sem suavização. Se `hold`, listar ações corretivas específicas com
responsável e prazo estimado. Se `promote`, listar condições de monitoramento
pós-deploy.

## 5. Notas de Implementação Globais
- Este épico é exclusivamente documental — nenhum código produzido
- O artefato `aflpd-validation-summary.md` é a entrega principal da fase
- A decisão final (`promote`/`hold`) é do PO — o épico apenas fornece a evidência
- Após decisão `promote`, as 4 fases devem ser movidas para `feito/` conforme SCRUM-GOV
