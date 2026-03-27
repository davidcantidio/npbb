---
doc_id: "FEATURE-4.md"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
project: "ATIVOS-INGRESSOS"
feature_key: "FEATURE-4"
feature_slug: "RECEBIMENTO-CONCILIACAO-E-BLOQUEIOS"
prd_path: "../../PRD-ATIVOS-INGRESSOS.md"
intake_path: "../../INTAKE-ATIVOS-INGRESSOS.md"
depende_de:
  - "FEATURE-2"
  - "FEATURE-3"
audit_gate: "not_ready"
---

# FEATURE-4 - Recebimento, conciliacao e bloqueios por ticketeira

> **Papel deste arquivo**: manifesto canonico da **Feature** versionado em Git, sob
> `features/FEATURE-4-RECEBIMENTO-CONCILIACAO-E-BLOQUEIOS/FEATURE-4.md`.

## 0. Rastreabilidade

- **Projeto**: `ATIVOS-INGRESSOS`
- **PRD**: [PRD-ATIVOS-INGRESSOS.md](../../PRD-ATIVOS-INGRESSOS.md) — sec. 2.3 (estados `recebido_confirmado`, `bloqueado_por_recebimento`, `disponivel`), 2.4 dentro (conciliacao, prevalencia recebido, bloqueio), 2.6 operacional externo, 4.1–4.2
- **Intake**: [INTAKE-ATIVOS-INGRESSOS.md](../../INTAKE-ATIVOS-INGRESSOS.md) — sec. 5, 6, 8
- **depende_de**: `FEATURE-2`, `FEATURE-3`

## 1. Objetivo de Negocio

- **Problema que esta feature resolve**: sem registrar o recebido confirmado e conciliar com o planejado, a operacao nao tem fonte de verdade para estoque distribuivel de ticketeiras nem bloqueios corretos para aumentos dependentes.
- **Resultado de negocio esperado**:
  - Para origem **externa recebida**, quantidade distribuivel reflete **recebido confirmado**, ainda que difira do planejado (PRD 2.4 / Intake 8).
  - Aumentos dependentes de ticketeira permanecem **bloqueados** ate recebimento correspondente.

## 2. Comportamento Esperado

- Operador ou integracao registra recebimentos (quantidades e/ou artefatos) vinculados a evento, diretoria, categoria e modo externo.
- Sistema calcula ou exibe divergencia **planejado vs recebido** de forma auditavel.
- Saldo **disponivel** para distribuicao externa respeita teto do recebido confirmado.
- Artefatos (arquivos, links, instrucoes textuais) persistidos com rastreabilidade minima alinhada a LGPD (detalhe de storage sujeito a dependencia pendente do PRD sec. 7).

## 3. Dependencias entre Features

- **depende_de**: [FEATURE-2](../FEATURE-2-DOMINIO-COEXISTENCIA-E-ROLOUT/FEATURE-2.md), [FEATURE-3](../FEATURE-3-CATEGORIAS-E-MODOS-FORNECIMENTO/FEATURE-3.md)

## 4. Criterios de Aceite

- [ ] Fluxo de registro de `recebido_confirmado` por lote ou registro equivalente documentado, com vinculo a categoria e modo externo.
- [ ] Regra de **prevalencia do recebido** aplicada para origem ticketeira em cenarios de divergencia (PRD 2.4).
- [ ] Estado `bloqueado_por_recebimento` aplicavel a aumentos dependentes ate recebimento correspondente (PRD 2.6).
- [ ] Leituras separadas nao misturam **remanejado** com aumento/reducao (orientacao PRD 3 — implementacao canonica documentada nesta feature ou em ADR vinculado).
- [ ] Trilha auditavel (quem/quando/o que) para alteracoes de recebimento e conciliacao.

## 5. Riscos Especificos

- Formatos heterogeneos de ticketeiras (PRD 5) — ingestao pode exigir normalizacao progressiva; contrato minimo deve ser explicitado.
- Politica de armazenamento LGPD pendente (PRD 3, 7) — criterios de aceite podem incluir placeholders controlados (ex.: referencia externa + metadados) ate decisao.

## 6. Estrategia de Implementacao

1. **Modelagem e migration**: recebimentos, divergencias, bloqueios, referencias a artefatos.
2. **API / backend**: endpoints para registro e consulta de saldos; alinhamento a FEATURE-7 para cargas automatizadas.
3. **UI / superficie**: telas de conciliacao e indicadores de bloqueio para operadores.
4. **Testes e evidencias**: cenarios divergencia planejado/recebido; bloqueio e liberacao apos recebimento.

## 7. Impacts por Camada

| Camada | Impacto | Detalhamento |
|--------|---------|----------------|
| Banco | Tabelas de recebimento, conciliacao, bloqueio | Indices por evento/categoria |
| Backend | Servicos de dominio de saldo | Regras de negocio centralizadas |
| Frontend | Fluxos de ativos/ingressos | Estados visiveis para operacao |
| Testes | Suites de dominio | Casos limite de divergencia |
| Observabilidade | Eventos de negocio | Correlation com FEATURE-2 |

## 8. Estado Operacional

- **status**: `todo`
- **audit_gate**: `not_ready`

## 9. User Stories (rastreabilidade)

| US ID | Titulo | SP estimado | Depende de | Status | Documento |
|-------|--------|-------------|------------|--------|-----------|
| US-4-01 | Modelo de persistencia de recebimento e conciliacao | 4 | FEATURE-2, FEATURE-3 | todo | [README.md](user-stories/US-4-01-MODELO-PERSISTENCIA-RECEBIMENTO/README.md) |
| US-4-02 | Registro de recebido confirmado | 4 | US-4-01 | todo | [README.md](user-stories/US-4-02-REGISTRO-RECEBIDO-CONFIRMADO/README.md) |
| US-4-03 | Prevalencia do recebido e teto distribuivel | 4 | US-4-02 | todo | [README.md](user-stories/US-4-03-PREVALENCIA-RECEBIDO-TETO-DISTRIBUIVEL/README.md) |
| US-4-04 | Estado bloqueado por recebimento | 4 | US-4-02, US-4-03 | todo | [README.md](user-stories/US-4-04-BLOQUEIO-POR-RECEBIMENTO/README.md) |
| US-4-05 | Leituras canonicas remanejado versus ajustes | 4 | US-4-03 (recomendado) | todo | [README.md](user-stories/US-4-05-LEITURAS-CANONICAS-REMANEJO-VS-AJUSTES/README.md) |
| US-4-06 | Superficie de conciliacao e indicadores de bloqueio | 5 | US-4-02, US-4-03, US-4-04 (recomendado) | todo | [README.md](user-stories/US-4-06-SUPERFICIE-CONCILIACAO-BLOQUEIOS/README.md) |

## 10. Referencias e Anexos

- PRD sec. 3 riscos de interpretacao sobre modelo canonico de conciliacao — fechar em ADR durante implementacao

---

## Checklist de prontidao do manifesto

- [x] `feature_key` e pasta alinhados
- [x] PRD e intake referenciados
- [x] `depende_de` correto
- [x] Criterios e impacts preenchidos
- [x] Tabela US apos decomposicao
