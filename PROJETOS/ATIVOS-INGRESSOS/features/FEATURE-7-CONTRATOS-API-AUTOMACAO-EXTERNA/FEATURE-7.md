---
doc_id: "FEATURE-7.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
project: "ATIVOS-INGRESSOS"
feature_key: "FEATURE-7"
feature_slug: "CONTRATOS-API-AUTOMACAO-EXTERNA"
prd_path: "../../PRD-ATIVOS-INGRESSOS.md"
intake_path: "../../INTAKE-ATIVOS-INGRESSOS.md"
depende_de:
  - "FEATURE-2"
  - "FEATURE-3"
  - "FEATURE-4"
audit_gate: "not_ready"
---

# FEATURE-7 - Contratos de API para automacao externa (ticketeiras)

> **Papel deste arquivo**: manifesto canonico da **Feature** versionado em Git, sob
> `features/FEATURE-7-CONTRATOS-API-AUTOMACAO-EXTERNA/FEATURE-7.md`.

## 0. Rastreabilidade

- **Projeto**: `ATIVOS-INGRESSOS`
- **PRD**: [PRD-ATIVOS-INGRESSOS.md](../../PRD-ATIVOS-INGRESSOS.md) — sec. 2.4 dentro (contratos para automacao), 2.7 fora (skill OpenClaw no repo), 4.2 (contratos, idempotencia, autenticacao), 6 fora
- **Intake**: [INTAKE-ATIVOS-INGRESSOS.md](../../INTAKE-ATIVOS-INGRESSOS.md) — sec. 6 dentro, 9, 12 fora skill no repo
- **depende_de**: `FEATURE-2`, `FEATURE-3`, `FEATURE-4`

## 1. Objetivo de Negocio

- **Problema que esta feature resolve**: recebimentos de ticketeiras chegam por canais externos; sem API estavel e segura, automacao (ex.: OpenClaw) nao pode alimentar o sistema de forma auditavel.
- **Resultado de negocio esperado**:
  - Integradores externos registram recebimentos e artefatos alinhados a **registry**, **ingestao inteligente** e **revisao humana** onde o PRD exige (sec. 2.7 / Intake 9).
  - Contratos documentados com limites de **idempotencia** e **autenticacao** (PRD 4.2).

## 2. Comportamento Esperado

- Endpoints ou jobs expostos para carga de dados compativel com o modelo de FEATURE-4.
- Nenhuma leitura de inbox nativa no NPBB (fora de escopo — PRD 2.4 fora).
- Nao desenvolver a skill OpenClaw neste repositorio (PRD 6 / Intake 12).

## 3. Dependencias entre Features

- **depende_de**: [FEATURE-2](../FEATURE-2-DOMINIO-COEXISTENCIA-E-ROLOUT/FEATURE-2.md), [FEATURE-3](../FEATURE-3-CATEGORIAS-E-MODOS-FORNECIMENTO/FEATURE-3.md), [FEATURE-4](../FEATURE-4-RECEBIMENTO-CONCILIACAO-E-BLOQUEIOS/FEATURE-4.md)

## 4. Criterios de Aceite

- [ ] Documentacao OpenAPI ou equivalente para operacoes de ingestao acordadas (payload, erros, codigos).
- [ ] Autenticacao de integrador (token, mTLS ou padrao ja usado no monolito) definida e testada.
- [ ] Idempotencia documentada para reenvios da mesma mensagem/fonte (chaves de deduplicacao).
- [ ] Fluxo opcional ou obrigatorio via registry / ingestao inteligente / revisao humana espelha integracoes internas citadas no PRD, sem implementar produto inbox.
- [ ] Cargas bem-sucedidas refletem em `recebido_confirmado` ou fila de revisao conforme desenho.

## 5. Riscos Especificos

- Formatos instaveis das ticketeiras (PRD 7) — contrato pode exigir camada de normalizacao ou validacao manual inicial.
- Excesso de escopo: esta feature nao substitui FEATURE-4, apenas expoe e integra.

## 6. Estrategia de Implementacao

1. **Modelagem e migration**: tabelas de idempotencia, chaves externas, filas se necessario.
2. **API / backend**: novos routers ou extensao sob namespace acordado; rate limit se aplicavel.
3. **UI / superficie**: workbench de revisao humana apenas se ja existir no produto — integrar, nao reinventar escopo PRD.
4. **Testes e evidencias**: contratos, seguranca, idempotencia, carga negativa.

## 7. Impacts por Camada

| Camada | Impacto | Detalhamento |
|--------|---------|----------------|
| Banco | Chaves de idempotencia, filas | |
| Backend | Novos endpoints, integracao registry | Segredos, escopos |
| Frontend | Possivel UI revisao | So se ja no escopo do produto |
| Testes | Contract tests, seguranca | |
| Observabilidade | Logs por integrador | correlation_id |

## 8. Estado Operacional

- **status**: `todo`
- **audit_gate**: `not_ready`

## 9. User Stories (rastreabilidade)

| US ID | Titulo | SP estimado | Depende de | Status | Documento |
|-------|--------|-------------|------------|--------|-----------|
| US-7-01 | Modelo de idempotencia e chaves externas | 2 | — | todo | [README.md](./user-stories/US-7-01-MODELO-IDEMPOTENCIA-E-CHAVES-EXTERNAS/README.md) |
| US-7-02 | Autenticacao do integrador | 2 | US-7-01 *(se credenciais no schema de 7-01; senao paralelo)* | todo | [README.md](./user-stories/US-7-02-AUTENTICACAO-INTEGRADOR/README.md) |
| US-7-03 | Endpoints de ingestao e fluxo operacional | 3 | US-7-01, US-7-02 | todo | [README.md](./user-stories/US-7-03-ENDPOINTS-INGESTAO-E-FLUXO-OPERACIONAL/README.md) |
| US-7-04 | OpenAPI, contrato e qualidade | 2 | US-7-03 | todo | [README.md](./user-stories/US-7-04-OPENAPI-CONTRATO-E-QUALIDADE/README.md) |

## 10. Referencias e Anexos

- PRD sec. 7 dependencias externas OpenClaw pending

---

## Checklist de prontidao do manifesto

- [x] `feature_key` e pasta alinhados
- [x] PRD e intake referenciados
- [x] `depende_de` correto
- [x] Criterios e impacts preenchidos
- [x] Tabela US apos decomposicao
