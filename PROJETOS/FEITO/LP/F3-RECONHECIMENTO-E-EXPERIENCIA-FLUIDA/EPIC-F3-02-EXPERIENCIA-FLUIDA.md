---
doc_id: "EPIC-F3-02-EXPERIENCIA-FLUIDA.md"
version: "1.1"
status: "done"
owner: "PM"
last_updated: "2026-03-12"
---

# EPIC-F3-02 - Experiência Fluida e "Registrar outro CPF"

## Objetivo

Lead reconhecido pula etapa CPF. Em ativação múltipla, vai direto ao formulário completo. Em ativação única quando já converteu, o GET landing precisa distinguir esse estado para então exibir opção "Registrar outro CPF" (ou "Cadastrar outra pessoa"). Conforme PRD seções 4, 5.3 e 5.4.

## Resultado de Negocio Mensuravel

Experiência fluida para leads recorrentes; ativação única permite registrar outro CPF quando o lead usa o celular para converter terceiros.

## Contexto Arquitetural

- GET landing retorna `lead_reconhecido`
- GET landing precisa expor flag explicita para "ja converteu nesta ativacao"
- Frontend: se lead_reconhecido, pular etapa CPF
- Ativação múltipla: formulário direto, submit registra nova conversão
- Ativação única + já converteu: mensagem "Você já se cadastrou" + link "Registrar outro CPF"
- Ao clicar "Registrar outro CPF": limpar estado e exibir CPF novamente

## Definition of Done do Epico

- [x] Lead reconhecido: pular etapa CPF, ir direto ao formulário
- [x] Ativação múltipla: formulário direto, submit registra nova conversão
- [x] Ativação única + já converteu: mensagem + opção "Registrar outro CPF"
- [x] Ao clicar "Registrar outro CPF": exibir CPF novamente para novo cadastro
- [x] Testes E2E cobrindo fluxos

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F3-02-001 | Lead reconhecido pula CPF e ativação múltipla | Pular CPF quando reconhecido; formulário direto em múltipla | 3 | done | [ISSUE-F3-02-001-LEAD-RECONHECIDO-PULA-CPF.md](./issues/ISSUE-F3-02-001-LEAD-RECONHECIDO-PULA-CPF.md) |
| ISSUE-F3-02-002.1 | Contrato do GET landing para "ja converteu nesta ativacao" | Expor no GET landing o sinal explicito que desbloqueia o fluxo de novo CPF | 2 | done | [ISSUE-F3-02-002.1-CONTRATO-GET-LANDING-JA-CONVERTEU.md](./issues/ISSUE-F3-02-002.1-CONTRATO-GET-LANDING-JA-CONVERTEU.md) |
| ISSUE-F3-02-002 | Opção "Registrar outro CPF" em ativação única | Exibir opção quando já converteu; fluxo para novo CPF | 2 | done | [ISSUE-F3-02-002-OPCAO-REGISTRAR-OUTRO-CPF.md](./issues/ISSUE-F3-02-002-OPCAO-REGISTRAR-OUTRO-CPF.md) |

## Artifact Minimo do Epico

- `backend/app/` (contrato GET landing)
- `backend/tests/` (testes de endpoint/contrato)
- `frontend/src/` (service layer e lógica de fluxo)
- `frontend/e2e/` (testes)

## Dependencias

- [EPIC-F3-01](./EPIC-F3-01-MECANISMO-RECONHECIMENTO.md)
- [F2](../F2-FLUXO-CPF-FIRST-E-CONVERSAO/F2_LP_EPICS.md)
- [PRD](../PRD-LP-QR-ATIVACOES.md)
- [Fase](./F3_LP_EPICS.md)
