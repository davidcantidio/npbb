# DOCX Como Spec de Dados

Este arquivo transforma o documento modelo de fechamento em um checklist de requisitos de dados. A intencao e que cada item abaixo vire um ou mais campos/tabelas no banco, com regras de calculo e linhagem para as fontes.

## Checklist (Contrato de Dados)

| Secao (DOCX) | Metrica/Conteudo esperado | Granularidade (evento/dia/sessao) | Tabelas/campos necessarios | Fonte atual no DOCX | Status |
|---|---|---|---|---|---|
| Contexto do evento | TODO | TODO | TODO | Secao "Contexto do evento" (template DOCX) | GAP |
| Objetivo do relatorio | TODO | TODO | TODO | Secao "Objetivo do relatorio" (template DOCX) | GAP |
| Fontes de dados e limitacoes | TODO | TODO | TODO | Secao "Fontes de dados e limitacoes" (template DOCX) | GAP |
| Big numbers (recorte analisado) | TODO | TODO | TODO | Secao "Big numbers (recorte analisado)" (template DOCX) | GAP |
| Publico do evento (controle de acesso - entradas validadas) | TODO | TODO | TODO | Secao "Publico do evento (controle de acesso - entradas validadas)" (template DOCX) | GAP |
| Dinamica de vendas (pre-venda) - shows (Opt-in aceitos) | TODO | TODO | TODO | Secao "Dinamica de vendas (pre-venda) - shows (Opt-in aceitos)" (template DOCX) | GAP |
| Quem sao clientes do Banco (proxy via categoria de ingresso - Opt-in) | TODO | TODO | TODO | Secao "Quem sao clientes do Banco (proxy via categoria de ingresso - Opt-in)" (template DOCX) | GAP |
| Perfil do publico (DIMAC - 12 a 14/12) | TODO | TODO | TODO | Secao "Perfil do publico (DIMAC - 12 a 14/12)" (template DOCX) | GAP |
| Satisfacao e percepcao (DIMAC) | TODO | TODO | TODO | Secao "Satisfacao e percepcao (DIMAC)" (template DOCX) | GAP |
| Pre-venda (leitura tecnica e aprendizados) | TODO | TODO | TODO | Secao "Pre-venda (leitura tecnica e aprendizados)" (template DOCX) | GAP |
| Performance nas redes (Instagram e social listening) | TODO | TODO | TODO | Secao "Performance nas redes (Instagram e social listening)" (template DOCX) | GAP |
| Midia e imprensa (MTC) | TODO | TODO | TODO | Secao "Midia e imprensa (MTC)" (template DOCX) | GAP |
| Leads e ativacoes (Festival de Esportes | 12-14/12) | TODO | TODO | TODO | Secao "Leads e ativacoes (Festival de Esportes | 12-14/12)" (template DOCX) | GAP |
| Recomendacoes (2026) - acoes tecnicas e de produto | TODO | TODO | TODO | Secao "Recomendacoes (2026) - acoes tecnicas e de produto" (template DOCX) | GAP |
| Apendice - definicoes rapidas | TODO | TODO | TODO | Secao "Apendice - definicoes rapidas" (template DOCX) | GAP |
| Shows por dia (12/12, 13/12, 14/12) | Para cada dia com show: entradas validadas, ingressos vendidos, opt-in aceitos e reconciliacao entre metricas | Dia e sessao (show) | `event_sessions` (tipo=show), `attendance_access_control`, `ticket_sales`, `optin_transactions` | Requisito obrigatorio de governanca (feedback de cobertura) | GAP |

## Figuras e Tabelas (Inventario do DOCX)

### Figuras (titulos)

- Entradas validadas (presentes) por sessao - 12 a 14/12/2025.
- Taxa de comparecimento por sessao (presentes/ingressos validos).
- Ingressos (opt-in aceitos) por dia de compra - sessoes 12/12 19h e 13/12 19h.
- Curva acumulada de vendas (% do total de ingressos por sessao).
- Ingressos por segmento (proxy de relacionamento BB) - sessoes com ticket (opt-in aceitos).
- Faixa etaria (DIMAC, n=491).
- Genero (DIMAC, n=491).
- Satisfacao geral (DIMAC).
- Participacao em acoes promovidas (DIMAC).
- Percepcao: evento aproxima do BB (DIMAC).
- Leads captados por dia (CPF unicos).
- Top ativacoes (contagem de participacoes).

### Tabelas

- Publico do evento (controle de acesso - entradas validadas): Campos esperados: `Sessao`, `Ingressos validos`, `Invalidos`, `Bloqueados`, `Presentes`, `Ausentes`, `Comparecimento`.

## Politica de Versionamento do Template e Spec

Esta politica esta codificada em `core/spec/policy.py`.

Regras de compatibilidade:
- Versao de schema em formato `major.minor`.
- Mesmo `major` da versao minima suportada.
- `minor` maior ou igual ao minimo suportado.

Versoes minimas:
- Spec schema minimo: `1.0`.
- Mapping schema minimo: `1.0`.

Artefatos padrao:
- `docs/analises/eventos/tamo_junto_2025/planning/00_docx_as_spec.md`
- `docs/analises/eventos/tamo_junto_2025/planning/03_requirements_to_schema_mapping.md`
- `docs/analises/eventos/tamo_junto_2025/planning/00_spec_diff.md`
- `docs/analises/eventos/tamo_junto_2025/planning/00_spec_diff.json`
- `core/spec/mapping_schema.yml`

## Processo de Mudanca e Validacao

1. Atualizar o template DOCX candidato e manter a baseline para comparacao.
2. Rodar diff entre versoes do template:
```bash
python -m etl.cli_spec spec:diff --old-docx <old.docx> --new-docx <new.docx> --out-md docs/analises/eventos/tamo_junto_2025/planning/00_spec_diff.md --out-json docs/analises/eventos/tamo_junto_2025/planning/00_spec_diff.json
```
3. Atualizar o checklist extraido:
```bash
python -m etl.cli_spec spec:extract --docx <new.docx> --out docs/analises/eventos/tamo_junto_2025/planning/00_docx_as_spec.md --format md
```
4. Revisar e atualizar o mapping em `core/spec/mapping_schema.yml`.
5. Regenerar documentacao de mapeamento:
```bash
python -m etl.cli_spec spec:render-mapping --docx <new.docx> --mapping core/spec/mapping_schema.yml --out docs/analises/eventos/tamo_junto_2025/planning/03_requirements_to_schema_mapping.md
```
6. Executar gate de spec antes de ETL/report:
```bash
python -m etl.cli_spec spec:gate --docx <new.docx> --mapping core/spec/mapping_schema.yml --required-section "Contexto do evento" --required-section "Objetivo do relatorio" --required-section "Publico do evento (controle de acesso - entradas validadas)" --required-section "Shows por dia (12/12, 13/12, 14/12)"
```
7. Bloquear promocao quando houver finding `error` e repetir o ciclo apos correcao.
