---
doc_id: "ISSUE-F1-03-001-PREPARAR-HANDOFF-PARA-REAUDITORIA.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
task_instruction_mode: "required"
decision_refs:
  - "auditoria_fluxo_ativacao.md / veredito hold e follow-ups"
  - "PRD-LP-REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA.md / escopo e riscos"
  - "ISSUE-F1-02-001 e ISSUE-F1-02-002 / evidencias consolidadas"
---

# ISSUE-F1-03-001 - Preparar handoff para reauditoria

## User Story

Como PM responsavel pelo sibling `REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA`, quero
um handoff curto e rastreavel para solicitar uma nova auditoria da F1 original
sem confundir esta trilha com reabertura de backlog funcional ou com uma
auditoria formal ja concluida.

## Contexto Tecnico

Depois das issues de baseline e evidencia, o sibling precisa fechar com uma
prestacao de contas objetiva: quais achados originais foram cobertos, quais
riscos continuam fora do escopo, quais evidencias a reauditoria deve receber e
por que o gate da F1 original permanece intocado ate nova rodada independente.
Esta issue toca apenas artefatos do sibling.

## Plano TDD

- Red: consolidar os resultados anteriores e verificar se o handoff ainda deixa lacunas para reauditoria
- Green: registrar resumo executivo, limites do sibling e checklist objetivo de reauditoria
- Refactor: confirmar que nenhum passo desta issue toca `AUDIT-LOG.md` ou o gate da F1 original

## Criterios de Aceitacao

- Given as issues anteriores concluidas, When o handoff for preparado, Then existe resumo executivo da remediacao e prestacao de contas dos achados originais
- Given os itens fora do sibling, When o handoff for lido, Then `backend/app/routers/leads.py` e LGPD de CPF em repouso aparecem explicitamente como fora do escopo
- Given a issue fechada, When a equipe pedir nova auditoria da F1 original, Then ha checklist objetivo de entradas esperadas para a reauditoria
- Given qualquer pressao para atualizar `AUDIT-LOG.md`, mudar o gate da F1 original ou ampliar backlog funcional, When isso surgir, Then a issue responde `BLOQUEADO`

## Definition of Done da Issue

- [ ] resumo executivo da remediacao consolidado
- [ ] prestacao de contas dos achados originais consolidada
- [ ] riscos fora do sibling explicitados
- [ ] checklist de reauditoria independente preparado
- [ ] ficou explicito que este sibling nao muda gate nem `AUDIT-LOG.md`

## Tasks Decupadas

- [ ] T1: consolidar o resumo executivo da remediacao e a prestacao de contas dos achados originais
- [ ] T2: explicitar o escopo fora do sibling e os riscos residuais
- [ ] T3: montar o checklist de reauditoria independente e o pacote de entradas esperadas

## Instructions por Task

### T1
- objetivo: transformar a baseline e as evidencias anteriores em resumo executivo curto e rastreavel
- precondicoes:
  - `ISSUE-F1-02-001` concluida
  - `ISSUE-F1-02-002` concluida
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/LP/auditoria_fluxo_ativacao.md`
  - `PROJETOS/LP/PRD-LP-REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA.md`
  - `PROJETOS/FEITO/LP/REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA/F1-BASELINE-E-REAUDITORIA-DO-HOLD/issues/ISSUE-F1-02-001-CONSOLIDAR-EVIDENCIA-DE-CONTRATO-E-PARIDADE.md`
  - `PROJETOS/LP/REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA/F1-BASELINE-E-REAUDITORIA-DO-HOLD/issues/ISSUE-F1-02-002-CONSOLIDAR-EVIDENCIA-DE-METADATA-E-THRESHOLD.md`
  - `PROJETOS/LP/REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA/F1-BASELINE-E-REAUDITORIA-DO-HOLD/issues/ISSUE-F1-03-001-PREPARAR-HANDOFF-PARA-REAUDITORIA.md`
- passos_atomicos:
  1. reler os achados do hold na auditoria original
  2. resumir, em linguagem objetiva, quais achados ja estao cobertos por baseline e evidencia deste sibling
  3. registrar a prestacao de contas dos achados originais sem reescrever o `AUDIT-LOG.md`
- comandos_permitidos:
  - `sed -n`
  - `rg -n`
  - `apply_patch`
- resultado_esperado: resumo executivo da remediacao e prestacao de contas dos achados do hold consolidados na issue
- testes_ou_validacoes_obrigatorias:
  - `rg -n "F1-NAO01|F1-NAO02|F1-NAO03|F1-NAO04|F1-NAO08|resumo|prestacao" PROJETOS/LP/REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA/F1-BASELINE-E-REAUDITORIA-DO-HOLD/issues/ISSUE-F1-03-001-PREPARAR-HANDOFF-PARA-REAUDITORIA.md`
- stop_conditions:
  - parar se a prestacao de contas exigir reinterpretar o veredito `hold`
  - parar se o resumo executivo depender de alterar artefato fora do sibling

### T2
- objetivo: explicitar os itens fora do sibling e os riscos residuais remanescentes
- precondicoes:
  - T1 concluida
  - resumo executivo consolidado
- arquivos_a_ler_ou_tocar:
  - `backend/app/routers/leads.py`
  - `PROJETOS/LP/PRD-LP-REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA.md`
  - `PROJETOS/LP/auditoria_fluxo_ativacao.md`
  - `PROJETOS/LP/REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA/F1-BASELINE-E-REAUDITORIA-DO-HOLD/issues/ISSUE-F1-03-001-PREPARAR-HANDOFF-PARA-REAUDITORIA.md`
- passos_atomicos:
  1. registrar `backend/app/routers/leads.py` como risco estrutural residual fora do sibling
  2. registrar LGPD de CPF em repouso como follow-up separado e fora do sibling
  3. explicitar que nenhum desses itens pode ser absorvido silenciosamente por esta trilha
- comandos_permitidos:
  - `wc -l`
  - `sed -n`
  - `apply_patch`
- resultado_esperado: lista objetiva de itens fora do sibling e riscos residuais consolidada
- testes_ou_validacoes_obrigatorias:
  - `wc -l backend/app/routers/leads.py`
- stop_conditions:
  - parar se houver pressao para incluir o refactor de `leads.py` nesta issue
  - parar se a discussao de LGPD passar de registro de risco para implementacao funcional

### T3
- objetivo: fechar a issue com checklist de reauditoria independente e pacote de entradas esperadas
- precondicoes:
  - T1 e T2 concluidas
  - limites do sibling consolidados
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/LP/REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA/F1-BASELINE-E-REAUDITORIA-DO-HOLD/F1_REMEDIAR_HOLD_F1_CONTRATO_ESTRUTURA_EPICS.md`
  - `PROJETOS/LP/F1-FUNDACAO-MODELO-BACKEND/F1_LP_EPICS.md`
  - `PROJETOS/LP/auditoria_fluxo_ativacao.md`
  - `PROJETOS/LP/REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA/F1-BASELINE-E-REAUDITORIA-DO-HOLD/issues/ISSUE-F1-03-001-PREPARAR-HANDOFF-PARA-REAUDITORIA.md`
- passos_atomicos:
  1. listar quais entradas a reauditoria independente deve receber: auditoria original, intake, PRD derivado, F1 original e as evidencias deste sibling
  2. registrar um checklist curto de leitura e validacao para a nova auditoria
  3. explicitar que a F1 original permanece em `hold` ate a nova rodada formal
- comandos_permitidos:
  - `apply_patch`
  - `sed -n`
  - `rg -n`
- resultado_esperado: handoff pronto para pedir reauditoria sem ambiguidade sobre escopo ou governanca
- testes_ou_validacoes_obrigatorias:
  - `rg -n "hold|reauditoria|AUDIT-LOG|leads.py|LGPD" PROJETOS/LP/REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA/F1-BASELINE-E-REAUDITORIA-DO-HOLD/issues/ISSUE-F1-03-001-PREPARAR-HANDOFF-PARA-REAUDITORIA.md`
- stop_conditions:
  - parar se a issue passar a exigir atualizacao de `AUDIT-LOG.md`
  - parar se o checklist depender de promover o gate da F1 original sem auditoria formal

## Arquivos Reais Envolvidos

- `PROJETOS/LP/auditoria_fluxo_ativacao.md`
- `PROJETOS/LP/PRD-LP-REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA.md`
- `PROJETOS/LP/F1-FUNDACAO-MODELO-BACKEND/F1_LP_EPICS.md`
- `backend/app/routers/leads.py`
- `PROJETOS/LP/REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA/F1-BASELINE-E-REAUDITORIA-DO-HOLD/F1_REMEDIAR_HOLD_F1_CONTRATO_ESTRUTURA_EPICS.md`
- `PROJETOS/FEITO/LP/REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA/F1-BASELINE-E-REAUDITORIA-DO-HOLD/issues/ISSUE-F1-02-001-CONSOLIDAR-EVIDENCIA-DE-CONTRATO-E-PARIDADE.md`
- `PROJETOS/LP/REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA/F1-BASELINE-E-REAUDITORIA-DO-HOLD/issues/ISSUE-F1-02-002-CONSOLIDAR-EVIDENCIA-DE-METADATA-E-THRESHOLD.md`

## Artifact Minimo

- handoff consolidado na propria issue, com resumo executivo, lista fora do sibling e checklist de reauditoria

## Dependencias

- [Issue de Evidencia de Contrato](./ISSUE-F1-02-001-CONSOLIDAR-EVIDENCIA-DE-CONTRATO-E-PARIDADE.md)
- [Issue de Evidencia de Metadata](./ISSUE-F1-02-002-CONSOLIDAR-EVIDENCIA-DE-METADATA-E-THRESHOLD.md)
- [Auditoria de Origem](../../../auditoria_fluxo_ativacao.md)
- [Epic](../EPIC-F1-03-HANDOFF-E-FECHAMENTO-DO-SIBLING.md)
- [Fase](../F1_REMEDIAR_HOLD_F1_CONTRATO_ESTRUTURA_EPICS.md)
