---
doc_id: "FEATURE-5.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
project: "ATIVOS-INGRESSOS"
feature_key: "FEATURE-5"
feature_slug: "EMISSAO-INTERNA-QR-UNITARIO"
prd_path: "../../PRD-ATIVOS-INGRESSOS.md"
intake_path: "../../INTAKE-ATIVOS-INGRESSOS.md"
depende_de:
  - "FEATURE-2"
  - "FEATURE-3"
audit_gate: "not_ready"
---

# FEATURE-5 - Emissao interna unitaria com QR

> **Papel deste arquivo**: manifesto canonico da **Feature** versionado em Git, sob
> `features/FEATURE-5-EMISSAO-INTERNA-QR-UNITARIO/FEATURE-5.md`.

## 0. Rastreabilidade

- **Projeto**: `ATIVOS-INGRESSOS`
- **PRD**: [PRD-ATIVOS-INGRESSOS.md](../../PRD-ATIVOS-INGRESSOS.md) — sec. 2.3 (`qr_emitido`, passos 3–4), 2.4 dentro (emissao interna, QR), 2.6 LGPD, 6 fora (validador QR completo), 4.1–4.2
- **Intake**: [INTAKE-ATIVOS-INGRESSOS.md](../../INTAKE-ATIVOS-INGRESSOS.md) — sec. 5–6, 14–15
- **depende_de**: `FEATURE-2`, `FEATURE-3`

## 1. Objetivo de Negocio

- **Problema que esta feature resolve**: ingressos internos sem identificador unico por destinatario impedem autenticidade e rastreio unitario; o PRD exige emissao a partir do **layout da categoria** com QR unico.
- **Resultado de negocio esperado**:
  - Cada destinatario de modo **interno emitido com QR** recebe registro unitario com identificador unico persistido.
  - Dados minimos para um **validador futuro** de uso unico ficam definidos (contrato minimo — PRD sec. 3), sem entregar o scanner no mesmo corte (PRD fora).

## 2. Comportamento Esperado

- A partir de categoria configurada (FEATURE-3), operador ou fluxo automatizado gera **ingresso unitario** por destinatario.
- QR (ou payload equivalente) associado ao registro; acesso restrito por RBAC.
- **Fora de escopo**: implementacao completa do validador na entrada do evento (PRD 2.4 fora / 6).

## 3. Dependencias entre Features

- **depende_de**: [FEATURE-2](../FEATURE-2-DOMINIO-COEXISTENCIA-E-ROLOUT/FEATURE-2.md), [FEATURE-3](../FEATURE-3-CATEGORIAS-E-MODOS-FORNECIMENTO/FEATURE-3.md)

## 4. Criterios de Aceite

- [ ] Emissao cria **um registro por destinatario** com identificador unico imutavel ou versionado de forma auditavel.
- [ ] Layout/visual da categoria aplicado na geracao conforme especificacao funcional (detalhe de template pode ser US posterior).
- [ ] Contrato de dados minimo para futura validacao documentado (payload QR, campos obrigatorios, sem inventar semantica fora do PRD/intake).
- [ ] Dados sensiveis tratados conforme LGPD (acesso, logs sem vazamento de payload completo em claro se politica exigir).
- [ ] Nao entrega scanner/validador de uso unico no portao (explicitamente fora do PRD neste corte).

## 5. Riscos Especificos

- Dependencia de estrategia de storage e retencao (PRD 7) para arquivos gerados e QR.
- Hipotese congelada PRD sec. 3: identidade persistida suficiente para validador futuro — pode exigir revisao quando o validador for escopo.

## 6. Estrategia de Implementacao

1. **Modelagem e migration**: tabela(s) de emissao unitaria, referencias a evento, diretoria, categoria, destinatario.
2. **API / backend**: emissao em lote ou individual; idempotencia onde aplicavel.
3. **UI / superficie**: fluxo em `/ingressos` ou modulo dedicado; preview quando aplicavel.
4. **Testes e evidencias**: unicidade por destinatario; tentativa de duplicidade; autorizacao.

## 7. Impacts por Camada

| Camada | Impacto | Detalhamento |
|--------|---------|----------------|
| Banco | Emissoes, possivel blob ou referencia externa | Conforme decisao de storage |
| Backend | Servico de emissao, integracao email saida se envio automatico | PRD 2.7 email ativo |
| Frontend | Formularios e listagens de emissoes | Estados `qr_emitido` |
| Testes | Unicidade, RBAC, regressao ingressos | |
| Observabilidade | Auditoria de emissao | correlation_id |

## 8. Estado Operacional

- **status**: `todo`
- **audit_gate**: `not_ready`

## 9. User Stories (rastreabilidade)

| US ID | Titulo | SP estimado | Depende de | Status | Documento |
|-------|--------|-------------|------------|--------|-----------|
| US-5-01 | Modelo e migracao de emissao unitaria | 5 | FEATURE-2, FEATURE-3 | todo | [README](user-stories/US-5-01-MODELO-E-MIGRACAO-EMISSAO-UNITARIA/README.md) |
| US-5-02 | Servico e API de emissao | 5 | US-5-01 | todo | [README](user-stories/US-5-02-SERVICO-E-API-EMISSAO/README.md) |
| US-5-03 | Contrato minimo do payload QR | 4 | US-5-01, US-5-02 | todo | [README](user-stories/US-5-03-CONTRATO-MINIMO-PAYLOAD-QR/README.md) |
| US-5-04 | UI operacional de emissao | 5 | US-5-02, US-5-03 | todo | [README](user-stories/US-5-04-UI-EMISSAO-OPERACIONAL/README.md) |

## 10. Referencias e Anexos

- Intake sec. 15 pergunta sobre contrato minimo QR — responder na implementacao/ADR

---

## Checklist de prontidao do manifesto

- [x] `feature_key` e pasta alinhados
- [x] PRD e intake referenciados
- [x] `depende_de` correto
- [x] Criterios e impacts preenchidos
- [x] Tabela US apos decomposicao
