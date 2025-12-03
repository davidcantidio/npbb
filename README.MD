# PRD – Sistema de Gestão de Eventos / Ativações / Leads / Ativos / Convites

## 0. Metadados do Projeto

- **Projeto**: Sistema de Gestão de Eventos / Ativações / Leads / Ingressos  
- **Versão do PRD**: 1.1  
- **Status**: Rascunho evolutivo  
- **Product Owner**: (preencher)  
- **Stakeholders**: Marketing, Promoção/Eventos, BI, TI, Dados  
- **Data**: (preencher)  
- **Objetivo**: Definir requisitos funcionais e técnicos do MVP para gestão completa de eventos, ativações, leads, cotas de ingressos, convites e convidados.

---

# 1. Visão Geral & Objetivo

## Problema / Oportunidade
O Banco do Brasil necessita de uma plataforma interna única que:

- Centralize dados de eventos, ativações, investimentos e leads.
- Permita gerar e monitorar cotas de ingressos para Diretorias.
- Controle convidadores (funcionários) e convidados vinculados às cotas.
- Integre-se com Salesforce para entrada de leads.
- Atenda requisitos de BI e monitoramento.

## Objetivo
Criar uma plataforma que ofereça:

- CRUD completo:
  - Eventos  
  - Ativações  
  - Investimentos  
  - Leads  
  - Convidados  
  - Convites  
  - Cotas de Ingressos (Ativos)  
- Página de **Ativos (Ingressos Cortesia)** com cards por Evento + Diretoria  
- Fluxo completo: convidadores → convidados → convites → consumo de ingressos  
- Página externa restrita (RUL) para funcionários convidarem pessoas  
- Dashboard operacional  
- Exportação CSV  
- Integração Salesforce  
- Backend + Frontend full stack (Node + React)  
- Banco PostgreSQL  

---

# 2. Usuários / Perfis

## Usuários Internos (~15)
- Marketing  
- Gerentes de eventos  
- Operações  
- BI  
- Administradores  

Acesso amplo no MVP.

## Usuários Convidadores (externo via RUL)
- Funcionários do BB usando **email @bb.com.br**
- Podem:
  - Criar conta
  - Cadastrar convidados
  - Emitir convites
  - Consumir ingressos da cota da sua Diretoria

---

# 3. Funcionalidades & Regras de Negócio

---

## 3.1 CRUD de Eventos
- Campos: nome, descrição, tipo/subtipo, cidade, estado, agência, diretoria, gestor  
- Datas previstas/realizadas  
- Público projetado/realizado  
- Status: previsto / em andamento / realizado / cancelado  
- Validação: subtipo pertence ao tipo (trigger existente)

---

## 3.2 CRUD de Ativações
- Cada ativação pertence a um evento  
- Campos: nome, descrição, valor  
- Relacionamento N:N com leads (`ativacao_lead`)

---

## 3.3 Investimentos
- Sempre vinculados a evento + ativação  
- Campos: tipo de investimento, descrição, valor  
- Sistema deve calcular:
  - Total geral por evento  
  - Total por tipo de investimento  

---

## 3.4 Leads (Integração Salesforce + armazenamento local)
- Formulário local → backend → Salesforce  
- Salesforce retorna ID externo (`salesforce_id`)  
- Lead gravado localmente com todos dados necessários  
- Permite listagem, filtros e exportação CSV  
- Associação com ativação via `ativacao_lead`

---

# 3.5 Ativos (Ingressos Cortesia) — *Nova Funcionalidade Principal*

### Interface
Substitui totalmente a página antiga de leads.

- Cards por **Evento + Diretoria**
- Cada card mostra:
  - **Título**: Nome do evento + diretoria
  - **Consumo**: `ingressos usados / ingressos disponíveis`
  - Barra de progresso
  - Botão **“Atribuir ingressos”**
  - Ação **“Ver convidados”**

### Regras
- **Ingressos usados = convites emitidos**
- Remover convidado devolve ingresso ao saldo
- Não pode definir cota menor que ingressos já usados
- Exportação CSV disponível  
- Filtros:
  - Evento  
  - Diretoria  

---

# 3.6 Convidadores (Funcionários — Página RUL)

### Cadastro
Acessam URL externa restrita.  
Campos obrigatórios:

- Nome  
- CPF  
- Email **@bb.com.br**  
- Diretoria  

Após cadastro, podem convidar pessoas para eventos em que sua Diretoria possua cotas.

---

# 3.7 Convidados
Cadastros feitos por convidadores.

Campos:
- Nome  
- CPF  
- Email  
- Telefone  
- Flag “É funcionário do banco?”  

Regras:
- Cada convidado consome **1 ingresso**  
- Remover convidado devolve ingresso  
- Salvar dados completos no banco  

---

# 3.8 Convites
Cada convidado = 1 convite.

Atributos:
- Evento  
- Diretoria  
- Funcionário convidador  
- Convidado  
- Status:
  - enviado  
  - pendente  
  - cancelado  

Regras:
- Convite só pode ser emitido se houver ingresso disponível  
- Remoção do convite:
  - Libera ingresso  
  - Remove convidado associado  

---

# 4. Modelo de Dados / Esquema

Manter tabelas:

- evento  
- ativacao  
- investimento  
- lead  
- ativacao_lead  
- convidado  
- convite  
- cota_cortesia  

### Inclusões
- `lead.salesforce_id`  
- Garantir relação:
  - cota_cortesia → convites emitidos (ingressos usados)  
  - convidado → convite  

---

# 5. Integração com Salesforce

- Backend envia lead para API Salesforce  
- Guarda `salesforce_id` retornado  
- Sem gravação local em caso de erro  
- Tratar token, expiração e erros da API  

---

# 6. Critérios de Aceitação / Qualidade

- CRUDs completos funcionando  
- Integração Salesforce funcionando  
- Dashboard funcionando com filtros  
- Página Ativos exibindo:
  - Cards corretos  
  - Consumo correto (usados/disponíveis)  
- Fluxo RUL funcionando para convidadores  
- Página de Convidados funcionando com remoção e devolução de ingressos  
- CSV funcionando para:
  - Eventos  
  - Leads  
  - Ativos  
  - Convidados  
- Banco consistente e sem registros órfãos  

---

# 7. Suposições & Dependências

- API Salesforce disponível  
- Funcionários usam email @bb.com.br  
- Volume do sistema compatível com stack proposta  
- MVP sem perfis avançados de permissão  
- Cotas dependem do preenchimento correto de `cota_cortesia`  

---

# 8. Roadmap / Backlog do MVP

| Nº | Feature | Prioridade |
|----|---------|-----------|
| 1 | Setup backend + banco | Alta |
| 2 | CRUD Evento | Alta |
| 3 | CRUD Ativação | Alta |
| 4 | CRUD Investimento | Alta |
| 5 | Integração Salesforce | Alta |
| 6 | CRUD Lead + associação Ativação | Média |
| 7 | **Página Ativos + lógica de cotas** | **Alta** |
| 8 | **Tela filha de Convidados + convites** | **Alta** |
| 9 | **Fluxo RUL: convidadores + cadastro de convidados** | **Alta** |
| 10 | Dashboard de eventos | Média |
| 11 | Exportações CSV | Alta |
| 12 | Testes automatizados | Média |
| 13 | Deploy | Alta |

---

# 9. Possíveis Evoluções Futuras

- Painel de check-in  
- QR Code para convidados  
- Permissões avançadas  
- Notificações automáticas  
- Relatórios customizados  

---

# 10. Layout

- **Material Design 3**  
- Tema claro/escuro  
- Componentes reativos e responsivos  

