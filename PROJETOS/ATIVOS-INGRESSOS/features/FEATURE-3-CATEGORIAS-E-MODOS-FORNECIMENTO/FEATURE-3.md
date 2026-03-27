---
doc_id: "FEATURE-3.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
project: "ATIVOS-INGRESSOS"
feature_key: "FEATURE-3"
feature_slug: "CATEGORIAS-E-MODOS-FORNECIMENTO"
prd_path: "../../PRD-ATIVOS-INGRESSOS.md"
intake_path: "../../INTAKE-ATIVOS-INGRESSOS.md"
depende_de:
  - "FEATURE-2"
audit_gate: "not_ready"
---

# FEATURE-3 - Categorias por evento e modos de fornecimento

> **Papel deste arquivo**: manifesto canonico da **Feature** versionado em Git, sob
> `features/FEATURE-3-CATEGORIAS-E-MODOS-FORNECIMENTO/FEATURE-3.md`.

## 0. Rastreabilidade

- **Projeto**: `ATIVOS-INGRESSOS`
- **PRD**: [PRD-ATIVOS-INGRESSOS.md](../../PRD-ATIVOS-INGRESSOS.md) — sec. 2.3 (fluxo), 2.4 dentro (categorias, dois modos canonicos), 4.1
- **Intake**: [INTAKE-ATIVOS-INGRESSOS.md](../../INTAKE-ATIVOS-INGRESSOS.md) — sec. 5, 6 dentro
- **depende_de**: `FEATURE-2`

## 1. Objetivo de Negocio

- **Problema que esta feature resolve**: hoje o sistema nao distingue categorias (pista, pista premium, camarote) nem modo de fornecimento (interno com QR vs externo recebido), o que impede conciliacao e emissao alinhadas ao negocio.
- **Resultado de negocio esperado**:
  - Por evento, a operacao configura o subconjunto do catalogo inicial necessario.
  - Cada linha operacional relevante associa-se a um **modo canonico** de fornecimento, condicionando regras posteriores (PRD sec. 2.3–2.4).

## 2. Comportamento Esperado

- Operador configura categorias disponiveis por evento (trio inicial; evento pode usar subset).
- Modos canonicos: **interno emitido com QR** e **externo recebido** estao modelados e selecionaveis onde o PRD exige.
- Leituras de UI/API distinguem categoria e modo para fluxos de FEATURE-4 e FEATURE-5.

## 3. Dependencias entre Features

- **depende_de**: [FEATURE-2](../FEATURE-2-DOMINIO-COEXISTENCIA-E-ROLOUT/FEATURE-2.md) *(dominio base e rollout)*

## 4. Criterios de Aceite

- [ ] Catalogo inicial pista / pista premium / camarote configuravel por evento, com subset permitido (PRD 2.4).
- [ ] Dois modos canonicos de fornecimento persistidos e expostos em API/contrato interno consumivel pelo frontend.
- [ ] Eventos legados sem configuracao mantem comportamento definido em FEATURE-2 (nao regressao).
- [ ] RBAC: apenas perfis autorizados alteram configuracao por evento (alinhado a restricoes LGPD/operacao do PRD 2.6).

## 5. Riscos Especificos

- Expansao futura do catalogo além do trio (Intake lacuna) — esta feature entrega apenas o inicial; mudancas de politica exigem PRD/intake atualizados.

## 6. Estrategia de Implementacao

1. **Modelagem e migration**: entidades de categoria por evento, vinculo a diretoria/area conforme PRD (Area equivalente a Diretoria em v1).
2. **API / backend**: CRUD ou endpoints de configuracao; validacao de modos.
3. **UI / superficie**: fluxos em `/ativos` ou telas dedicadas conforme desenho UX; alinhamento ao padrao existente.
4. **Testes e evidencias**: casos por evento com subset de categorias; modo interno vs externo.

## 7. Impacts por Camada

| Camada | Impacto | Detalhamento |
|--------|---------|----------------|
| Banco | Tabelas de configuracao por evento | FKs para evento, diretoria, enums de modo |
| Backend | Novos endpoints ou extensao de `ativos` | Validacao, erros 4xx claros |
| Frontend | `AtivosList` / fluxos relacionados | Filtros e formularios de configuracao |
| Testes | Novos + regressao | Cobrir ambos os modos |
| Observabilidade | Logs de alteracao de config | Auditoria operacional |

## 8. Estado Operacional

- **status**: `todo`
- **audit_gate**: `not_ready`

## 9. User Stories (rastreabilidade)

| US ID | Titulo | SP estimado | Depende de | Status | Documento |
|-------|--------|-------------|------------|--------|-----------|
| US-3-01 | Modelagem persistida de categorias e modos canonicos | 5 | FEATURE-2 | todo | [README.md](./user-stories/US-3-01-MODELAGEM-PERSISTENCIA-E-DEFAULTS-LEGADO/README.md) |
| US-3-02 | API de configuracao, RBAC e exposicao dos modos canonicos | 5 | US-3-01 | todo | [README.md](./user-stories/US-3-02-API-CONFIGURACAO-RBAC-E-CONTRATO-MODOS/README.md) |
| US-3-03 | UI de configuracao de categorias por evento | 3 | US-3-02 | todo | [README.md](./user-stories/US-3-03-UI-CONFIGURACAO-CATEGORIAS-POR-EVENTO/README.md) |
| US-3-04 | Regressao FEATURE-2, testes e observabilidade de config | 3 | US-3-02; US-3-03 para cenarios UI | todo | [README.md](./user-stories/US-3-04-REGRESSAO-TESTES-E-OBSERVABILIDADE-CONFIG/README.md) |

## 10. Referencias e Anexos

- PRD sec. 2.3 estados `planejado` e passo 1 do fluxo ponta a ponta

---

## Checklist de prontidao do manifesto

- [x] `feature_key` e pasta alinhados
- [x] PRD e intake referenciados
- [x] `depende_de` reflete FEATURE-2
- [x] Criterios de aceite e impacts preenchidos
- [x] Tabela de User Stories apos decomposicao
