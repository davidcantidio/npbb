# Épicos — Ajuste Fino Landing Pages Dinâmicas / F2 — Rastreabilidade Backend
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** AJUSTE-FINO-LANDING-PAGES-DINAMICAS | **fase:** F2
**prd:** ../PRD-LANDING-REDESIGN-ATIVACAO-v1.2.md
**status:** aprovado

---
## Objetivo da Fase
Criar a infraestrutura backend para rastreabilidade completa de gamificação: migration
dos campos `gamificacao_id`, `gamificacao_completed` e `gamificacao_completed_at` em
`AtivacaoLead`, extensão do payload da landing com dados de ativação e gamificações,
retorno de `ativacao_lead_id` no submit, e criação do endpoint
`POST /ativacao-leads/{id}/gamificacao`.

Ao final da fase, o backend serve o payload estendido com ativação e gamificações,
retorna `ativacao_lead_id` no submit do lead, e aceita a chamada de conclusão de
gamificação com persistência correta.

## Épicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F2-01 | Migration AtivacaoLead — Campos de Gamificação | Adicionar 3 campos nullable a `AtivacaoLead` via migration Alembic sem lock de tabela. | nenhuma | 🔲 | `EPIC-F2-01-MIGRATION-ATIVACAO-LEAD-GAMIFICACAO.md` |
| EPIC-F2-02 | Extensão Payload Landing e Endpoint Gamificação | Estender payload do GET landing com ativação e gamificações, retornar `ativacao_lead_id` no POST submit e criar endpoint de conclusão de gamificação. | EPIC-F2-01 | 🔲 | `EPIC-F2-02-EXTENSAO-PAYLOAD-E-ENDPOINT-GAMIFICACAO.md` |

## Dependências entre Épicos
`EPIC-F2-01` → `EPIC-F2-02`

O EPIC-F2-02 depende da migration do EPIC-F2-01 porque os campos de gamificação em
`AtivacaoLead` são necessários para o endpoint de conclusão e para o retorno no submit.

## Definition of Done da Fase
- [ ] Tabela `ativacao_lead` possui campos `gamificacao_id`, `gamificacao_completed`, `gamificacao_completed_at` (todos nullable)
- [ ] Migration aplica sem erro em banco limpo e com dados existentes
- [ ] Rollback remove campos sem efeito colateral
- [ ] `GET /ativacoes/{id}/landing` retorna `ativacao` com `nome`, `descricao`, `mensagem_qrcode`
- [ ] `GET /ativacoes/{id}/landing` retorna `gamificacoes` como array (vazio quando sem gamificação)
- [ ] `POST /leads/` retorna `ativacao_lead_id` na response
- [ ] `POST /ativacao-leads/{id}/gamificacao` persiste `gamificacao_id`, `gamificacao_completed` e `gamificacao_completed_at`
- [ ] Nenhum campo removido do payload existente de template
- [ ] Testes de contrato atualizados e passando

## Notas e Restrições
- Todos os campos novos são nullable/com default — sem lock de tabela em produção
- `gamificacoes` é sempre array no payload — vazio (`[]`) quando não há gamificação
- Endpoint de gamificação é público, protegido por opacidade do `ativacao_lead_id`
- Nenhuma alteração em `LeadConversao`
