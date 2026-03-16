---
doc_id: "INTAKE-SUPABASE.md"
version: "1.0"
status: "draft"
owner: "PM"
last_updated: "2026-03-16"
project: "SUPABASE"
intake_kind: "refactor"
source_mode: "original"
origin_project: "nao_aplicavel"
origin_phase: "nao_aplicavel"
origin_audit_id: "nao_aplicavel"
origin_report_path: "nao_aplicavel"
product_type: "platform-capability"
delivery_surface: "backend-api"
business_domain: "autenticacao"
criticality: "alta"
data_sensitivity: "interna"
integrations:
  - "Supabase"
  - "Alembic"
  - "PostgreSQL"
change_type: "migracao"
audit_rigor: "standard"
---

# INTAKE - SUPABASE

> Migração do PostgreSQL local para Supabase (schema + dados), substituindo o estado desatualizado do Supabase pelo estado atual do código e dados locais.

## 0. Rastreabilidade de Origem

- projeto de origem: nao_aplicavel
- fase de origem: nao_aplicavel
- auditoria de origem: nao_aplicavel
- relatorio de origem: nao_aplicavel
- motivo da abertura deste intake: decisão de migrar do PostgreSQL local para Supabase antes do deploy (Render + Supabase + Cloudflare)

## 1. Resumo Executivo

- nome curto da iniciativa: Migração PostgreSQL local → Supabase
- tese em 1 frase: Supabase como única fonte de banco de dados, refletindo o estado atual do código e dados locais.
- valor esperado em 3 linhas:
  - Deixar de usar PostgreSQL local completamente; Supabase como único banco.
  - Schema e dados migrados; Supabase substituído pelo estado do PostgreSQL local.
  - Deploy unificado (Render + Supabase + Cloudflare) desbloqueado.

## 2. Problema ou Oportunidade

- problema atual: uso dual (PostgreSQL local vs Supabase); schema e dados desatualizados no Supabase; deploy bloqueado.
- evidencia do problema: projeto Supabase existe com schema antigo; código usa ~50 migrations Alembic em estado local; histórico Supabase → local → alterações → retorno.
- custo de nao agir: deploy permanece bloqueado; inconsistência entre ambientes.
- por que agora: processo de contratação, hospedagem e compra de domínio em andamento; necessidade de ambiente unificado antes do go-live.

## 3. Publico e Operadores

- usuario principal: desenvolvedor/operador que fará o deploy e manutenção
- usuario secundario: nao_aplicavel
- operador interno: nao_aplicavel
- quem aprova ou patrocina: PM

## 4. Jobs to be Done

- job principal: substituir PostgreSQL local por Supabase; migrar schema e dados; dados locais substituem os do Supabase.
- jobs secundarios: garantir que migrations Alembic apliquem corretamente no Supabase; validar conexão e testes.
- tarefa atual que sera substituida: uso de PostgreSQL local para desenvolvimento e como fonte de verdade.

## 5. Fluxo Principal Desejado

Descreva o fluxo ponta a ponta em etapas curtas:

1. Garantir que o schema local seja aplicado no Supabase (migrations Alembic ou equivalente).
2. Exportar dados do PostgreSQL local (pg_dump ou ferramenta adequada).
3. Substituir dados do Supabase pelos dados locais (import, truncate + reload conforme estratégia).
4. Validar: backend conectando ao Supabase; testes passando; dados consistentes.
5. Remover dependência do PostgreSQL local; configurar DATABASE_URL/DIRECT_URL para Supabase.

## 6. Escopo Inicial

### Dentro

- Migrations Alembic aplicadas no Supabase
- Migração de dados (schema + dados) do PostgreSQL local para Supabase
- Configuração DATABASE_URL (pooler :6543) e DIRECT_URL (direct :5432)
- Validação de conexão e testes
- Remoção da dependência do PostgreSQL local

### Fora

- Integração com Supabase Auth (manter auth própria do backend: JWT/SECRET_KEY)
- Mudanças de modelo de dados além do merge
- Alterações no frontend

## 7. Resultado de Negocio e Metricas

- objetivo principal: Supabase como único banco, refletindo o estado atual do código e dados locais.
- metricas leading: migrations aplicadas sem erro; dados exportados/importados com sucesso.
- metricas lagging: backend conectando ao Supabase; testes passando; deploy desbloqueado.
- criterio minimo para considerar sucesso: backend em produção usando Supabase; PostgreSQL local não mais necessário; dados consistentes.

## 8. Restricoes e Guardrails

- restricoes tecnicas: preservar compatibilidade com Alembic; não quebrar testes com SQLite (TESTING=true); manter auth própria do backend.
- restricoes operacionais: nao_definido
- restricoes legais ou compliance: nao_aplicavel
- restricoes de prazo: nao_definido
- restricoes de design ou marca: nao_aplicavel

## 9. Dependencias e Integracoes

- sistemas internos impactados: backend (app/db), config (.env), alembic
- sistemas externos impactados: Supabase (hosted PostgreSQL)
- dados de entrada necessarios: dump/export do PostgreSQL local; credenciais Supabase (DATABASE_URL, DIRECT_URL)
- dados de saida esperados: Supabase populado com schema e dados atualizados

## 10. Arquitetura Afetada

- backend: config de conexão (database.py), variáveis de ambiente
- frontend: nao_aplicavel (não altera)
- banco/migracoes: principal; migrations Alembic; script ou processo de migração de dados
- observabilidade: nao_definido
- autorizacao/autenticacao: manter auth própria; não integrar Supabase Auth
- rollout: nao_definido

## 11. Riscos Relevantes

- risco de produto: nao_aplicavel
- risco tecnico: conflito de schema; migrations falhando em ordem diferente
- risco operacional: downtime durante migração
- risco de dados: perda de dados na substituição (mitigado: dados locais são a fonte; Supabase pode ser substituído)
- risco de adocao: nao_aplicavel

## 12. Nao-Objetivos

- Refatorar modelos de dados
- Integrar Supabase Auth
- Alterar frontend
- Mudar estratégia de deploy além do banco

## 13. Contexto Especifico para Problema ou Refatoracao

- sintoma observado: uso de PostgreSQL local; Supabase com schema e dados desatualizados; deploy bloqueado.
- impacto operacional: ambiente fragmentado; impossibilidade de deploy com stack planejada (Render + Supabase + Cloudflare).
- evidencia tecnica: ~50 migrations Alembic em backend/alembic/versions/; backend/.env.example com DATABASE_URL/DIRECT_URL; alembic/env.py suporta Supabase.
- componente(s) afetado(s): alembic, backend/app/db/database.py, backend/.env
- riscos de nao agir: deploy permanece bloqueado; inconsistência entre ambientes; dificuldade de onboarding.

## 14. Lacunas Conhecidas

- regra de negocio ainda nao definida: nenhuma crítica
- dependencia ainda nao confirmada: nenhuma
- dado ainda nao disponivel: nenhum
- decisao de UX ainda nao fechada: nao_aplicavel
- outro ponto em aberto: estratégia exata de export/import de dados (pg_dump, ordem de tabelas, FKs) será detalhada no PRD

## 15. Perguntas que o PRD Precisa Responder

- Qual a estratégia exata de export/import de dados (pg_dump, ordem de execução, tratamento de FKs)?
- Qual a ordem de execução: schema primeiro ou schema + dados em conjunto?
- Como proceder em caso de rollback (restore do Supabase a partir de backup)?

## 16. Checklist de Prontidao para PRD

- [x] intake_kind esta definido
- [x] source_mode esta definido
- [x] rastreabilidade de origem esta declarada ou marcada como nao_aplicavel
- [x] problema esta claro
- [x] publico principal esta claro
- [x] fluxo principal esta descrito
- [x] escopo dentro/fora esta fechado
- [x] metricas de sucesso estao declaradas
- [x] restricoes estao declaradas
- [x] dependencias e integracoes estao declaradas
- [x] arquitetura afetada esta mapeada
- [x] riscos relevantes estao declarados
- [x] lacunas conhecidas estao declaradas
- [x] contexto especifico de problema/refatoracao foi preenchido quando aplicavel
