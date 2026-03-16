---
doc_id: "EPIC-F2-02-Recarregar-o-Supabase-com-os-Dados-Locais.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-16"
---

# EPIC-F2-02 - Recarregar o Supabase com os dados locais

## Objetivo

Executar a substituicao dos dados atuais do Supabase pelos dados do PostgreSQL
local seguindo o runbook aprovado, com ordem segura de limpeza/import e
validacao pos-carga suficiente para liberar o cutover.

## Resultado de Negocio Mensuravel

- os dados antigos do Supabase sao substituidos pelo estado atual do PostgreSQL local
- a ordem operacional da recarga respeita dependencias e evita improviso em ambiente sensivel
- a fase F3 recebe um banco alvo consistente e com rollback viavel

## Contexto Arquitetural

- a F1 ja validou o schema do Supabase e a F2-01 entrega os artefatos de backup e export
- o backend usa `DATABASE_URL` no runtime e `DIRECT_URL` para operacoes sensiveis de banco, o que impacta a forma de executar carga e validacoes
- `docs/SETUP.md`, `docs/TROUBLESHOOTING.md` e `backend/scripts/seed_common.py` ja centralizam premissas operacionais relevantes para a migracao

## Definition of Done do Epico
- [ ] recarga de dados executada conforme o runbook aprovado
- [ ] integridade pos-carga validada antes de liberar o cutover
- [ ] rollback mantido como caminho operacional viavel ate a validacao final

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F2-02-001 | Implementar recarga controlada de dados no Supabase | Executar limpeza e import com ordem segura e comandos reproduziveis | 5 | done | [ISSUE-F2-02-001-Implementar-Recarga-Controlada-de-Dados-no-Supabase.md](./issues/ISSUE-F2-02-001-Implementar-Recarga-Controlada-de-Dados-no-Supabase.md) |
| ISSUE-F2-02-002 | Validar integridade pos-carga e procedimento de rollback | Confirmar que o Supabase agora reflete os dados locais e que o retorno e viavel se necessario | 3 | todo | [ISSUE-F2-02-002-Validar-Integridade-Pos-Carga-e-Procedimento-de-Rollback.md](./issues/ISSUE-F2-02-002-Validar-Integridade-Pos-Carga-e-Procedimento-de-Rollback.md) |

## Artifact Minimo do Epico

- recarga executada sobre o Supabase
- checklist de integridade pos-carga preenchido
- rollback mantido pronto ate a liberacao de F3

## Dependencias
- [Intake](../INTAKE-SUPABASE.md)
- [PRD](../PRD-SUPABASE.md)
- [Fase](./F2_SUPABASE_EPICS.md)
- [EPIC-F2-01](./EPIC-F2-01-Preparar-Backup-e-Export-do-PostgreSQL-Local.md)
