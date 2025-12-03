# PRD – Sistema de Gestão de Eventos / Ativações / Leads

## 0. Metadados do Projeto

- **Projeto**: Sistema de Gestão de Eventos / Ativações / Leads – versão interna Banco do Brasil  
- **Versão do PRD**: 1.0  
- **Status**: Rascunho  
- **Product Owner**: (preencher)  
- **Stakeholders principais**: Marketing, Equipe de Promoção/Eventos, BI, Engenharia, Dados  
- **Data do documento**: (preencher)  
- **Objetivo**: definir escopo, requisitos e estrutura para o MVP do sistema  

## 1. Visão Geral & Objetivo

**Problema / Oportunidade**  
Atualmente existe um sistema web de cadastro de eventos e ativações, mas há necessidade de consolidar dados para BI, adotar um sistema próprio com melhorias, integrar leads via API externa, e armazenar histórico de dados.

**Objetivo do produto**  
Construir um sistema interno que permita: CRUD completo de eventos, ativações, investimentos, leads, convidados e convites; integração com API externa (Salesforce) para captura de leads + armazenamento local; dashboard/listagens para gestão; exportação de dados.

**Escopo do MVP**  

- CRUD de Eventos, Ativações, Investimentos, Leads, Convidados, Convites  
- Envio de lead via integração com API externa + gravação local com ID externo  
- Listagens / filtros básicos para entidades  
- Dashboard/listagem de eventos com resumo e filtros  
- Exportação de dados via CSV  

**Fora do escopo (inicial)**  

- Gamificação  
- Sistema de permissões/papéis refinado  
- Dashboards complexos com gráficos, BI embutido  
- Automação de marketing ou notificações complexas  
- Check-in com QR code (por ora, apenas lista de presença simples)

## 2. Usuários / Perfis

- Usuários internos (~ 15): equipe de marketing/promoção/eventos, BI, operações  
- Acesso amplo e igualitário (sem níveis de permissão diferenciados no MVP)

## 3. Funcionalidades & Regras de Negócio

### 3.1 CRUD de Eventos  
- Campos: nome, descrição, tipo/subtipo, cidade, estado, agência, diretoria, gestor, data prevista de início/fim, data realizada de início/fim (opcional), público projetado, público realizado (opcional), status (previsto, realizado, cancelado, em andamento).  
- Validação de consistência: subtipo só válido se pertencer ao tipo.  
- Data real / público real e outros campos de resultado opcionais até pós-evento.

### 3.2 CRUD de Ativações  
- Cada ativação vinculada a um evento.  
- Campos básicos: nome, descrição, valor de investimento (se aplicável).  
- Possibilidade de associar leads (N:N via tabela de pivô).  

### 3.3 Investimentos  
- Sempre vinculados a evento + ativação.  
- Campos: tipo de investimento (patrocínio / promoção), descrição, valor.  
- O sistema deve calcular automaticamente:  
  - Total investido por evento  
  - Totais separados por tipo de investimento  

### 3.4 Leads (Integração externa + armazenamento local)  
- Formulário de lead: front envia dados ao backend → backend envia para API externa (Salesforce).  
- Ao receber sucesso, extrair `salesforce_id` e demais dados → gravar localmente na tabela `lead`.  
- Permitir listar leads e associar a ativações por meio de tabela de pivô.  

### 3.5 Exportação CSV  
- Permitir exportar, com filtros, os dados de eventos, ativações, investimentos, leads.  

### 3.6 Dashboard / Listagens  
- Página tabular de eventos com filtros por data, status, tipo, agência, diretoria, cidade, estado, gestor etc.  
- Colunas de resumo: número de ativações, total investido, total leads (quando aplicável), status do evento, datas previstas/realizadas.  

## 4. Modelo de Dados / Esquema de Banco

Baseado no schema existente, com adição mínima:

- Adicionar campo `salesforce_id` (string) na tabela `lead` para armazenar o ID retornado pela API externa.  
- Manter tabelas: evento, ativacao, investimento, lead, ativacao_lead, convidado, convite, cota_cortesia (se for relevante), etc.  
- Preservar campos de datas previstas/realizadas, público projetado/realizado, status do evento conforme definido.  

## 5. Integração com API Externa (Salesforce)

- Backend (Node) terá endpoint para receber dados de lead vindos do front.  
- Backend consome API externa conforme documentação, cria lead, recebe ID externo.  
- Armazena lead local com `salesforce_id` + demais campos relevantes.  
- Tratamento de erros: se criação no Salesforce falhar → retorna erro para front, não salva no banco local.  
- Considerar autenticação e renovação de token se API usar OAuth ou mecanismo similar.

## 6. Critérios de Aceitação / Qualidade para MVP

- CRUDs funcionando corretamente (criação, leitura, edição, exclusão) para todas entidades do escopo.  
- Integração com API externa: lead enviado com sucesso → lead visível no sistema + ID externo salvo corretamente.  
- Listagens e filtros funcionando.  
- Exportação CSV funcionando e exporta os dados filtrados corretamente.  
- Dashboard tabular exibindo eventos com colunas de resumo corretas.  
- Cálculo de total de investimentos por evento e por tipo está correto.  
- Banco consistente, sem dados órfãos ou inconsistentes, integridade preservada.

## 7. Suposições & Dependências

- A API externa de leads (Salesforce) estará disponível e funcionando conforme documentação.  
- Não haverá necessidade imediata de controle fino de permissões ou hierarquia de acesso.  
- Volume previsto (~ 1000 eventos/ano, ~ 1800 ativações) cabe sem problemas em uma instância PostgreSQL + backend padrão.  
- Os ~15 usuários internos têm perfil homogêneo, sem necessidade de roles distintas.  

## 8. Roadmap / Backlog do MVP

| Nº | Tarefa / Feature | Prioridade |
|----|------------------|------------|
| 1  | Configuração do projeto backend + banco (schema / migrations) | Alta |
| 2  | CRUD para Evento (backend + modelos) | Alta |
| 3  | CRUD para Ativação | Alta |
| 4  | CRUD para Investimento | Alta |
| 5  | CRUD para Lead (local) + campo `salesforce_id` | Alta |
| 6  | Endpoint + integração com API externa para criação de lead | Alta |
| 7  | Implementar associação Lead ↔ Ativação (pivô) | Média-Alta |
| 8  | Frontend React – telas CRUD (Evento, Ativação, Investimento, Lead) | Alta |
| 9  | Frontend React – listagens + filtros | Alta |
| 10 | Exportação CSV (backend + front) | Média |
| 11 | Dashboard de eventos (tabela + filtros + resumos) | Média |
| 12 | Testes (unitários backend, integração API, testes front-end básicos) | Média |
| 13 | Preparar infraestrutura / deploy / configuração inicial | Alta |

## 9. Possíveis Evoluções / Versões Futuras (após MVP)

- Dashboards com gráficos / KPIs visuais  
- Controle de permissões / papéis / níveis de acesso  
- Check-in / Lista de presença com relatórios  
- Relatórios customizados / filtros avançados / exportações detalhadas  
- Logs de auditoria / histórico de alterações  
- UI/UX refinada, melhorias visuais e de usabilidade  

