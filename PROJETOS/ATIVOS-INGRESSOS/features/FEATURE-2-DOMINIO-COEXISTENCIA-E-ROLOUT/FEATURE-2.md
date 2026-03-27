---
doc_id: "FEATURE-2.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
project: "ATIVOS-INGRESSOS"
feature_key: "FEATURE-2"
feature_slug: "DOMINIO-COEXISTENCIA-E-ROLOUT"
prd_path: "../../PRD-ATIVOS-INGRESSOS.md"
intake_path: "../../INTAKE-ATIVOS-INGRESSOS.md"
depende_de: []
audit_gate: "not_ready"
---

# FEATURE-2 - Dominio, coexistencia com legado e rollout

> **Papel deste arquivo**: manifesto canonico da **Feature** versionado em Git, sob
> `features/FEATURE-2-DOMINIO-COEXISTENCIA-E-ROLOUT/FEATURE-2.md`. O PRD descreve problema, objetivo,
> escopo, restricoes e rollout global **sem** listar features nem user stories;
> **este documento** consolida a feature entregavel, dependencias entre features,
> criterios de aceite e impacto por camada. User Stories e Tasks ficam em
> `user-stories/` apos as etapas de decomposicao do pipeline.

## 0. Rastreabilidade

- **Projeto**: `ATIVOS-INGRESSOS`
- **PRD**: [PRD-ATIVOS-INGRESSOS.md](../../PRD-ATIVOS-INGRESSOS.md) — sec. 2.4 (dentro/fora), 2.6 (restricoes tecnicas e rollout), 4.0 (baseline), 4.1, 8
- **Intake**: [INTAKE-ATIVOS-INGRESSOS.md](../../INTAKE-ATIVOS-INGRESSOS.md) — sec. 8, 10, 12
- **depende_de**: nenhuma *(espelho do frontmatter)*

## 1. Objetivo de Negocio

- **Problema que esta feature resolve**: sem um alicerce de dominio e estrategia de convivencia, qualquer evolucao em categorias, recebimento ou QR arrisca quebrar `CotaCortesia` / `SolicitacaoIngresso` e telas atuais antes de um corte operacional validado.
- **Resultado de negocio esperado**:
  - O produto pode evoluir por **evento** (ou equivalente documentado) sem desligar o fluxo agregado legado ate o rollout acordado.
  - Existe trilha minima (`correlation_id` ou equivalente) entre operacoes que antecedem features posteriores, alinhada ao PRD.

## 2. Comportamento Esperado

- Equipa tecnica e operacao tem **criterio explicito** de ativacao do novo modelo por evento (feature flag ou mecanismo equivalente descrito na implementacao).
- Dados e rotas legadas continuam **funcionais** para eventos nao migrados, conforme restricao do PRD.
- Modelo canonico inicial (entidades/tabelas ou adaptacao) existe para suportar **FEATURE-3+**, com migracao versionada e plano de rollback alinhado ao PRD sec. 8.

## 3. Dependencias entre Features

- **depende_de**: [] *(espelho do frontmatter; manter alinhado)*

## 4. Criterios de Aceite

- [ ] Documentacao viva (ou ADR) descreve convivencia entre modelo agregado atual e o novo dominio ate o rollout; referencia o baseline em `PRD-ATIVOS-INGRESSOS.md` sec. 4.0.
- [ ] Mecanismo de **ativacao gradual por evento** implementado e testado em ambiente de integracao.
- [ ] Migracoes aplicaveis nao removem dados reconciliados em cenario de rollback descrito no PRD (sec. 8), salvo decisao documentada.
- [ ] Ponto de extensao para `correlation_id` (ou padrao equivalente) definido para fluxos que FEATURE-4 a FEATURE-8 irao reutilizar.

## 5. Riscos Especificos

- Complexidade de migracao dual-write ou backfill se o primeiro corte exigir dados historicos nas novas entidades.
- Indefinicao de politica de storage (PRD sec. 3 e 7) pode atrasar persistencia de binarios; esta feature nao resolve LGPD sozinha, mas nao deve impedir rollout do dominio base.

## 6. Estrategia de Implementacao

1. **Modelagem e migration**: introduzir esqueleto de entidades alinhado ao PRD sec. 4.1 / Intake sec. 10; preservar unicidade e comportamento atual de `CotaCortesia` onde aplicavel.
2. **API / backend**: manter contratos existentes de `/ativos` e `/ingressos` para eventos nao migrados; preparar extensao ou rotas paralelas conforme desenho posterior.
3. **UI / superficie**: sem mudanca obrigatoria de UX nesta feature, salvo indicadores de "evento no novo fluxo" se necessario para operacao.
4. **Testes e evidencias**: testes de regressao dos endpoints baseline (PRD sec. 4.0); testes do gate de rollout por evento.

## 7. Impacts por Camada

| Camada | Impacto | Detalhamento |
|--------|---------|----------------|
| Banco | Novas tabelas ou colunas de transicao | Constraints, indices, estrategia de migracao de dados existentes |
| Backend | Convivencia de routers e servicos | `ativos.py`, `ingressos.py`, modelos em `models.py` sem quebrar clientes atuais |
| Frontend | Opcional | Flags ou rotas condicionais por evento, se exigido |
| Testes | `test_ativos_endpoints`, `test_ingressos_endpoints` + novos | Baseline PRD 4.0 |
| Observabilidade | Correlation / request id | Logging estruturado para encadear FEATURE-4–8 |

## 8. Estado Operacional

- **status**: `todo`
- **audit_gate**: `not_ready`

## 9. User Stories (rastreabilidade)

| US ID | Titulo | SP estimado | Depende de | Status | Documento |
|-------|--------|-------------|------------|--------|-----------|
| US-2-01 | ADR e convivencia legado versus novo dominio | 2 | — | todo | [README.md](./user-stories/US-2-01-ADR-E-COEXISTENCIA/README.md) |
| US-2-02 | Modelo canonico inicial e migracoes seguras | 5 | US-2-01 (reco) | todo | [README.md](./user-stories/US-2-02-MODELO-E-MIGRACOES-INICIAIS/README.md) |
| US-2-03 | Ativacao gradual por evento (feature gate) | 4 | US-2-02 | todo | [README.md](./user-stories/US-2-03-ROLLOUT-POR-EVENTO/README.md) |
| US-2-04 | Correlation ID e ponto de extensao para fluxos futuros | 3 | US-2-02 (paralelo OK) | todo | [README.md](./user-stories/US-2-04-CORRELATION-E-EXTENSAO/README.md) |
| US-2-05 | Regressao do baseline ativos e ingressos | 4 | US-2-02, US-2-03 | todo | [README.md](./user-stories/US-2-05-REGRESSAO-BASELINE-ATIVOS-INGRESSOS/README.md) |

## 10. Referencias e Anexos

- `backend/docs/auditoria_eventos/ATIVOS_STATE_NOW.md`, `docs/auditoria_eventos/RESTORE_ATIVOS_SUMMARY.md` (baseline citado no PRD)

---

## Checklist de prontidao do manifesto

- [x] `feature_key` e pasta `FEATURE-2-DOMINIO-COEXISTENCIA-E-ROLOUT/` alinhados com `GOV-FRAMEWORK-MASTER.md`
- [x] PRD e intake referenciados com caminhos relativos corretos
- [x] `depende_de` reflete ordem real entre features
- [x] Criterios de aceite verificaveis e impacts por camada preenchidos
- [x] Tabela de User Stories atualizada quando US forem criadas ou renomeadas
