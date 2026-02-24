# TMJ 2025 - Guia Detalhado de Dry-Run

## Objetivo
Executar localmente um fluxo completo de validacao do fechamento TMJ 2025, usando apenas fixtures e sem depender de dados reais.

O script cobre:
- extracao (`XLSX`, `PDF`, `PPTX`);
- seed de catalogo/ingestao e sessoes esperadas;
- preflight de qualidade e cobertura;
- geracao de `report.docx` e `manifest.json`.

Arquivo principal:
- `scripts/dry_run_tmj_pipeline.py`

## Quando usar
- Antes de integrar novos extractors no fluxo principal.
- Antes de alterar gates de DQ/coverage/report.
- Para validar se o encadeamento `ETL -> DQ -> coverage -> Word` continua funcional.

## Pre-requisitos
- Executar a partir da raiz do repo: `npbb/`.
- Ambiente Python com dependencias instaladas.
- Fixtures locais disponiveis em `tests/fixtures`.

Comando minimo de verificacao:
```bash
python scripts/dry_run_tmj_pipeline.py --help
```

## Execucao basica
Comando recomendado:
```bash
python scripts/dry_run_tmj_pipeline.py --out-dir reports/tmj2025/dry_run
```

Resultado esperado no terminal:
- mensagem `[OK] dry-run TMJ pipeline concluido`;
- caminhos dos 4 artefatos finais.

## Parametros do script
- `--out-dir`
  Diretorio de saida de artefatos e temporarios.
- `--event-id`
  `event_id` do fluxo de preflight/report. Padrao: `2025`.
- `--fixtures-root`
  Raiz dos fixtures. Padrao: `tests/fixtures`.
- `--optin-xlsx`
  Fixture XLSX do extractor de opt-in.
- `--leads-xlsx`
  Fixture XLSX do extractor de leads.
- `--access-pdf`
  Fixture PDF para extracao assistida de controle de acesso.
- `--agenda-path`
  Agenda master usada para semear sessoes esperadas.

Exemplo com caminhos explicitos:
```bash
python scripts/dry_run_tmj_pipeline.py \
  --out-dir reports/tmj2025/dry_run_custom \
  --event-id 2025 \
  --fixtures-root tests/fixtures \
  --optin-xlsx tests/fixtures/xlsx/optin_min.xlsx \
  --leads-xlsx tests/fixtures/xlsx/leads_min.xlsx \
  --access-pdf tests/fixtures/pdf/min_table.pdf \
  --agenda-path tests/fixtures/agenda/agenda_master_min.yml
```

## O que o dry-run executa internamente
1. Roda extractors de fixture:
- `extract_xlsx_optin_aceitos`;
- `extract_xlsx_leads_festival`;
- `extract_pptx_slide_text` (com PPTX minimo gerado em runtime);
- `extract_pdf_assisted` (template de acesso).

2. Cria banco local SQLite em:
- `<out-dir>/dry_run.sqlite`

3. Semeia tabelas operacionais para preflight:
- `sources`;
- `ingestions`;
- `event_sessions` (a partir da agenda master).

4. Roda preflight antes do Word:
- `dq:run` gerando `dq_report.json`;
- avaliacao de coverage gerando `coverage_report.json`.

5. Roda `report:render` com `--run-preflight` e gera:
- `report.docx`;
- `report_manifest.json`.

6. Copia o manifest final para nome padrao do dry-run:
- `manifest.json`.

## Artefatos gerados
No diretorio `--out-dir`, o fluxo finaliza com:
- `dq_report.json`
  Resultado de checks e secoes de DQ.
- `coverage_report.json`
  Status por sessao/dataset (inclui gaps/parciais de show).
- `report.docx`
  Documento Word renderizado no fluxo de preflight.
- `manifest.json`
  Manifest de auditoria do relatorio.

Artefatos auxiliares:
- `dry_run.sqlite` (banco local isolado do dry-run);
- `report_manifest.json` (gerado pelo renderer e copiado para `manifest.json`);
- pasta `staging/` com saidas de extractors;
- pasta `fixtures_runtime/` com PPTX minimo gerado em tempo de execucao;
- `template_dry_run.docx` (template minimo para teste de render).

## Como validar rapidamente
Checklist tecnico:
- `dq_report.json` existe e tem `summary` e `sections`;
- `coverage_report.json` existe e tem `sessions` (lista);
- `report.docx` existe e abre sem placeholder pendente;
- `manifest.json` existe e tem `event_id`.

Comando de teste automatizado:
```bash
pytest -q tests/test_dry_run_tmj_pipeline.py
```

## Troubleshooting
Erro de fixture ausente:
- Sintoma: `[ERROR] Fixture nao encontrado (...)`.
- Acao: conferir caminhos passados via CLI e existencia em `tests/fixtures`.

Falha no render com preflight:
- Sintoma: erro vindo de `report:render` ou gate.
- Acao: abrir `dq_report.json` e `coverage_report.json` do mesmo `out-dir` e validar findings de severidade.

Erro de import de modulo:
- Sintoma: `ModuleNotFoundError`.
- Acao: executar o comando a partir da raiz `npbb/` e validar ambiente Python com dependencias instaladas.

## Fixtures padrao usadas
- `tests/fixtures/xlsx/optin_min.xlsx`
- `tests/fixtures/xlsx/leads_min.xlsx`
- `tests/fixtures/pdf/min_table.pdf`
- `tests/fixtures/agenda/agenda_master_min.yml`

## Limites do dry-run
- Nao substitui execucao com fontes reais do evento.
- Nao valida qualidade estatistica de negocio em profundidade.
- Focado em integridade de orquestracao, artefatos e gate basico de fluxo.
