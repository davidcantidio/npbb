# Evidencias canonicas da integracao do cache da analise etaria

Esta pasta e o destino canonico das evidencias da
`FEATURE-10-INTEGRACAO-CACHE-ANALISE-ETARIA` e dos gates de `phase-f4`.

Uso recomendado para scripts diagnosticos:

- passar `--out-dir artifacts/phase-f4/evidence`
- ou exportar `LEADS_AUDIT_EVIDENCE_DIR=artifacts/phase-f4/evidence`

Exemplos:

- `cd backend && LEADS_AUDIT_EVIDENCE_DIR=../artifacts/phase-f4/evidence python scripts/profile_dashboard_age_analysis.py --label phase-f4`
- `cd backend && LEADS_AUDIT_EVIDENCE_DIR=../artifacts/phase-f4/evidence python scripts/run_critical_explains.py --profile dashboard_age --label phase-f4`
- `cd backend && LEADS_AUDIT_EVIDENCE_DIR=../artifacts/phase-f4/evidence python scripts/capture_pg_stat_statements.py --profile dashboard_age_analysis --label phase-f4`

Historico:

- `auditoria/evidencias/` continua guardando artefatos antigos e nao deve ser
  apagada nem reinterpretada como fonte canonica desta feature nova.
