# Docs - Index

Esta e a porta de entrada da documentacao do projeto. Se estiver com pressa, siga o **README** e o **SETUP**.

## Comece por aqui
- `../README.MD` - visao geral + comandos rapidos
- `SETUP.md` - setup completo (backend + frontend)
- `DEPLOY_RENDER_CLOUDFLARE.md` - deploy publico (Render API + Cloudflare Pages)
- `WORKFLOWS.md` - fluxos principais (importacao assistida por dominio, dashboard, relatorio)
- `TROUBLESHOOTING.md` - problemas comuns e como resolver
- `ARCHITECTURE.md` - visao rapida de modulos e fronteiras

## APIs e contratos (referencias detalhadas)
- `auth.md` - login, JWT e recuperacao de senha
- `eventos_api.md` - eventos
- `formulario_lead_api.md` - formularios de leads
- `gamificacao_api.md` - gamificacao
- `ativacoes_api.md` - ativacoes
- `leads_importacao.md` - importacao CSV/XLSX
- `publicidade_importacao.md` - importacao assistida de publicidade (core reutilizavel)
- `leads_conversoes.md` - regras de conversao

## ETL - Runbooks de Sprint
- `etl/contrato_canonico_s1.md` - runbook operacional CONT S1
- `etl/contrato_canonico_s2.md` - runbook operacional CONT S2
- `etl/contrato_canonico_s3.md` - runbook operacional CONT S3
- `etl/contrato_canonico_s4.md` - fluxo principal e gate de regressao CONT S4
- `etl/motor_confianca_s1.md` - runbook operacional CONF S1
- `etl/motor_confianca_s2.md` - runbook operacional CONF S2
- `etl/motor_confianca_s3.md` - runbook operacional CONF S3
- `etl/motor_confianca_s4.md` - fluxo principal e guardrails de tuning CONF S4

## Dashboard e relatorios
- `tela-inicial/menu/Dashboard/leads_dashboard.md` - contrato do dashboard de leads (backend)
- `roadmap_dashboard_import_batch.md` - roadmap tecnico
- `../reports/README.md` - como gerar o DOCX do Festival TMJ 2025
- `../reports/RESTORE_SUMMARY.md` - resumo de restauracao
- `etl/tmj2025_dry_run_usage.md` - guia detalhado do dry-run TMJ 2025 (ETL -> DQ -> coverage -> Word)

## Especificacoes de UI (legacy)
Estes arquivos descrevem telas e podem divergir do codigo atual. Use como referencia visual e valide no app.
- `tela-inicial/tela_inicial.md`
- `tela-inicial/menu/Eventos/eventos.md`
- `tela-inicial/menu/Ativos/ativos.md`
- `tela-inicial/menu/Eventos/Detalhes_Evento/detalhes_evento.md`
- `tela-inicial/menu/Eventos/Novo evento/form_evento/form_novo_evento.md`
- `tela-inicial/menu/Eventos/Novo evento/form_formulario_leads/form_formulario_leads.md`
- `tela-inicial/menu/Eventos/Novo evento/form_ativacao/form_ativacao.md`
- `tela-inicial/menu/Eventos/Novo evento/form_gamificacao/form_gamificacao.md`
- `tela-inicial/menu/Eventos/Novo evento/form_questionario/form_questionario.md`
- `login/login.md`
- `login/new_user/login_tela_inicial.md`

## PRDs / ADRs
TODO (nao encontrado no repo): adicionar PRD/ADR oficial ou apontar para o repositorio correto.

## Arquivados
- `docs/_archive/` - materiais legados (templates e notas antigas)
