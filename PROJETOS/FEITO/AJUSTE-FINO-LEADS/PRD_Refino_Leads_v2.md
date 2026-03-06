# PRD — Refinamentos da Seção de Leads

**Produto:** Sistema de Gestão de Leads (NPBB)  
**Área:** Dashboard > Leads · /leads pipeline  
**Tipo:** Refino de funcionalidades existentes + nova funcionalidade  
**Status:** Em definição  
**Data:** 2025-06-03  
**Revisão:** v2 — confrontada com codebase (frontend + e2e)

---

## 1. Contexto

Este documento consolida melhorias identificadas na seção de Leads do sistema, coletadas a partir de sessão de revisão com a equipe de produto. Os itens cobrem correções de UX, integridade de dados, ajustes de API e novas capacidades de exportação.

### Mapeamento técnico do sistema atual

| Área | Localização no código |
|---|---|
| Batch upload (bronze) | `POST /leads/batches` · `createLeadBatch()` em `leads_import.ts` |
| Mapeamento (silver) | `POST /leads/batches/:id/mapear` · `mapearLeadBatch()` |
| Pipeline (gold) | `POST /leads/batches/:id/executar-pipeline` · `executarPipeline()` |
| Dashboard Leads | `GET /dashboard/leads` · `DashboardLeads.tsx` · `getDashboardLeadsReport()` |
| Listagem de leads | `GET /leads` (redirects para `/leads/importar`) |
| Seleção de evento p/ mapeamento | `GET /leads/referencias/eventos` · `listReferenciaEventos()` |
| Estágios do batch | `stage: "bronze" \| "silver" \| "gold"` (internamente em inglês) |

---

## 2. Escopo

As melhorias cobrem:

- Formulário de upload de batch de leads (campo `data_envio`)
- Dropdown de correspondência Evento ↔ Lead (`listReferenciaEventos`)
- Modelo de dados de `LeadListItem` (campos ausentes)
- Fluxo de criação rápida de evento durante mapeamento
- Exportação de leads em estágio **gold** a partir do Dashboard de Leads

---

## 3. Requisitos Funcionais

### 3.1 Data padrão no formulário de upload de batch

**Contexto técnico:** O formulário de upload de leads envia `data_envio` para `POST /leads/batches` via `createLeadBatch()`. Atualmente o campo não tem valor padrão, forçando o usuário a preencher manualmente.

**Comportamento esperado:**
- Ao abrir o formulário de upload, o campo `data_envio` deve ser pré-preenchido com a data de hoje no formato `YYYY-MM-DD` (padrão da API).
- O usuário pode alterar a data manualmente, caso necessário.
- O campo nunca deve ficar em branco ao abrir o formulário.

**Impacto no código:**
- Frontend: inicializar o estado do campo `data_envio` com `new Date().toISOString().slice(0, 10)` na página de upload de batch (provavelmente em `ImportacaoPage` ou componente pai).

**Critério de aceite:**
- [ ] Campo `data_envio` pré-preenchido com a data atual ao abrir o formulário.
- [ ] Campo permanece editável.
- [ ] `POST /leads/batches` recebe `data_envio` com a data correta mesmo sem edição manual.

---

### 3.2 Data do evento no dropdown de seleção de evento

**Contexto técnico:** O endpoint `GET /leads/referencias/eventos` (via `listReferenciaEventos()`) retorna atualmente apenas `{ id: number; nome: string }`. O dropdown de mapeamento de leads exibe apenas o nome, sem distinguir eventos de mesmo nome ou informar o período.

**Comportamento esperado:**
- Cada opção do dropdown exibe: `[Nome do Evento] — [Data de início]`
- Exemplo: `Workshop de Vendas — 15/05/2025`
- Data deve ser formatada em `DD/MM/YYYY` para exibição.
- A ordenação padrão deve ser por data de início decrescente (mais recente no topo).

**Impacto no código:**
- Backend: estender resposta de `GET /leads/referencias/eventos` para incluir `data_inicio_prevista: string | null`.
- Frontend: atualizar o tipo de retorno de `listReferenciaEventos()` em `leads_import.ts` para `{ id: number; nome: string; data_inicio_prevista: string | null }[]`.
- Componente de dropdown: formatar label como `${nome} — ${formatDate(data_inicio_prevista)}`.

**Critério de aceite:**
- [ ] Endpoint retorna `data_inicio_prevista` em todos os itens.
- [ ] Dropdown exibe nome + data em todas as opções.
- [ ] Eventos sem data exibem apenas o nome (sem erro/crash).
- [ ] Ordenação por data decrescente como padrão.

---

### 3.3 Recuperação de campos removidos do modelo de Lead

**Contexto técnico:** O tipo `LeadListItem` em `leads_import.ts` e o banco de dados atual não possuem os seguintes campos que existiam em modelos anteriores do sistema:

```typescript
// LeadListItem atual — campos ausentes identificados:
// sobrenome, rg, genero, logradouro, numero, complemento, bairro, cep
```

Os campos identificados como ausentes são:

| Campo | Tipo sugerido | Observação |
|---|---|---|
| `sobrenome` | `string \| null` | Pode estar fundido no campo `nome` atual |
| `rg` | `string \| null` | Documento de identidade |
| `genero` | `string \| null` | Ex: `"M"`, `"F"`, `"Outro"` |
| `logradouro` | `string \| null` | Endereço — rua |
| `numero` | `string \| null` | Endereço — número |
| `complemento` | `string \| null` | Endereço — complemento |
| `bairro` | `string \| null` | Endereço — bairro |
| `cep` | `string \| null` | CEP sem máscara |
| `cidade` | `string \| null` | **Já existe** em `LeadListItem` |
| `estado` | `string \| null` | **Já existe** em `LeadListItem` |

> **Nota:** `cidade` e `estado` já estão presentes. O foco é nos campos completamente ausentes.

**Impacto no código:**
- Backend: avaliar se a tabela de leads já possui colunas (`sobrenome`, `rg`, `genero`, campos de endereço) e se apenas estão ausentes da serialização, ou se precisam ser migradas/adicionadas.
- Backend: adicionar os campos ao schema de resposta do endpoint de listagem de leads.
- Frontend: estender `LeadListItem` em `leads_import.ts` com os campos acima.
- CSV de importação (`leads-import-smoke.csv`): fixture atual usa `nome,email,cpf,evento_nome` — novos campos devem ser opcionais e backward-compatible.

**Critério de aceite:**
- [ ] Campos listados acima disponíveis no modelo de dados de leads.
- [ ] Campos exibíveis e editáveis no perfil do lead.
- [ ] Importação de CSV existente não quebra com a adição dos novos campos (retrocompatibilidade).
- [ ] Migração de banco documentada ou script de migration gerado.

---

### 3.4 Criação rápida de evento durante mapeamento de lead

**Contexto técnico:** Durante o fluxo de mapeamento de leads (`POST /leads/batches/:id/mapear`), o usuário precisa informar um `evento_id`. Se o evento não existe ainda, o usuário perde o contexto do mapeamento para criar o evento em outra tela. O endpoint `POST /evento/` está funcional (confirmado nos smoke tests em `leads-evento.api.smoke.spec.ts`).

**Comportamento esperado:**
- Ao pesquisar no dropdown de eventos e não encontrar resultado, exibir opção: **"+ Criar evento rapidamente"**.
- Ao clicar, abrir um modal/drawer com formulário mínimo:

| Campo | Obrigatório | Observação |
|---|---|---|
| `nome` | Sim | Nome do evento |
| `data_inicio_prevista` | Sim | Formato `YYYY-MM-DD` |
| `cidade` | Sim | Já exigido pela API |
| `estado` | Sim | Sigla UF, já exigido pela API |
| `diretoria_id` | Sim | Buscar do catálogo `GET /evento/all/diretorias` |
| `concorrencia` | Não | Default `false` |

- Após salvar (`POST /evento/`), o evento recém-criado é automaticamente selecionado no dropdown de mapeamento em curso.
- O evento pode ser editado com mais detalhes depois via `/eventos/:id/editar`.

**Impacto no código:**
- Frontend: adicionar lógica de "opção especial" no Autocomplete/Select de evento no fluxo de mapeamento.
- Frontend: criar componente `QuickCreateEventoModal` reutilizável.
- Frontend: chamar `POST /evento/` e em seguida recarregar `listReferenciaEventos()`.
- Nenhuma mudança de backend necessária (endpoint já existe).

**Critério de aceite:**
- [ ] Opção "Criar evento rapidamente" visível quando nenhum resultado é encontrado no dropdown.
- [ ] Modal contém apenas os campos essenciais da tabela acima.
- [ ] Após criação, o evento é automaticamente selecionado no mapeamento em curso.
- [ ] Evento criado aparece na listagem completa em `/eventos`.
- [ ] Erro de criação exibe mensagem sem perder o estado do mapeamento em andamento.

---

## 4. Nova Funcionalidade — Exportação de Leads em Estágio Gold

### 4.1 Descrição

A partir do **Dashboard de Leads** (`/dashboard/leads` · `DashboardLeads.tsx`), o usuário deve conseguir exportar os dados dos leads cujos batches se encontram no estágio **`gold`** (fase Ouro na UI), com a possibilidade de filtrar por evento específico ou exportar todos de uma vez.

### 4.2 Terminologia técnica

> O sistema usa **`gold`** internamente (campo `stage` do modelo `LeadBatch`). A interface exibe **"Ouro"** como label para o usuário final. Este PRD usa os dois termos, sendo `gold` o valor usado em chamadas de API.

### 4.3 Localização na interface

> `Dashboard` → `Leads` (`/dashboard/leads`) → Botão **"Exportar Leads Ouro"**

O botão deve ser adicionado na seção superior do `DashboardLeads.tsx`, preferencialmente ao lado dos botões "Aplicar" / "Limpar" do filtro existente, ou como ação separada com destaque visual.

### 4.4 Fluxo de exportação

1. Usuário acessa `/dashboard/leads`.
2. Clica no botão **"Exportar Leads Ouro"**.
3. Um modal é exibido com:

   **Selecionar Evento:**
   - Reutiliza o mesmo Autocomplete de eventos do filtro existente.
   - Opção fixa no topo: `Todos os eventos`.

   **Formato de exportação:**
   - `.xlsx` (padrão)
   - `.csv` (separador `;` para compatibilidade pt-BR)

4. Usuário seleciona evento (ou "Todos") e formato.
5. Clica em **"Exportar"**.
6. Arquivo é gerado no backend e download iniciado automaticamente via Blob URL.

### 4.5 Novo endpoint de backend

```
GET /leads/export/gold
```

**Query params:**

| Parâmetro | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `evento_id` | `integer` | Não | Filtrar por evento específico |
| `formato` | `"xlsx" \| "csv"` | Não (default: `xlsx`) | Formato do arquivo de saída |

**Response:** Arquivo binário com header `Content-Disposition: attachment; filename="leads_ouro_..."`

**Lógica de filtro no backend:**
- Selecionar leads cujo batch associado tem `stage = "gold"` E `pipeline_status IN ("pass", "pass_with_warnings")`.
- Se `evento_id` informado: filtrar pelo evento vinculado ao lead (campo `evento_nome` ou join com batch).
- Se `evento_id` ausente: retornar todos os leads gold.

### 4.6 Novo serviço de frontend

Adicionar em `leads_import.ts` (ou novo arquivo `leads_export.ts`):

```typescript
export async function exportLeadsGold(
  token: string,
  params: { evento_id?: number; formato?: "xlsx" | "csv" },
): Promise<Blob> { ... }
```

### 4.7 Dados incluídos na exportação

| Coluna no arquivo | Campo na API | Observação |
|---|---|---|
| Nome completo | `nome` | Campo atual de `LeadListItem` |
| E-mail | `email` | Campo atual |
| CPF | `cpf` | Campo atual |
| Telefone | `telefone` | Campo atual |
| Evento de origem | `evento_nome` | Campo atual |
| Cidade | `cidade` | Campo atual |
| Estado | `estado` | Campo atual |
| Data de compra | `data_compra` | Campo atual |
| Data de criação | `data_criacao` | Campo atual |
| Sobrenome | `sobrenome` | Depende da entrega do item 3.3 |
| Gênero | `genero` | Depende da entrega do item 3.3 |
| RG | `rg` | Depende da entrega do item 3.3 |
| Endereço | `logradouro`, `cep`, etc. | Depende da entrega do item 3.3 |
| Estágio | — | Valor fixo `"Ouro"` em todas as linhas |

> Campos marcados como "Depende do item 3.3" devem ser incluídos com valor vazio se a entrega 3.3 não estiver disponível no mesmo ciclo.

### 4.8 Nomeclatura do arquivo exportado

| Seleção | Nome do arquivo |
|---|---|
| Todos os eventos | `leads_ouro_todos_YYYY-MM-DD.xlsx` |
| Evento específico | `leads_ouro_[slug-do-evento]_YYYY-MM-DD.xlsx` |

### 4.9 Regras de negócio

- Apenas leads vinculados a batches com `stage = "gold"` devem constar.
- Pipeline reprovado (`pipeline_status = "fail"`) não deve ser exportado.
- Se nenhum lead for encontrado para a seleção, retornar HTTP 204 e exibir toast: _"Nenhum lead em fase Ouro encontrado para os filtros selecionados."_
- Separador CSV: `;` (padrão Brasil).
- Encoding: UTF-8 com BOM para compatibilidade com Excel.

### 4.10 Critérios de aceite

- [ ] Botão "Exportar Leads Ouro" visível no `DashboardLeads.tsx`.
- [ ] Modal de exportação exibe seleção de evento com opção "Todos".
- [ ] `GET /leads/export/gold` filtra corretamente por `stage = "gold"`.
- [ ] Arquivo gerado contém as colunas da tabela 4.7.
- [ ] Nome do arquivo segue o padrão da tabela 4.8.
- [ ] Estado vazio (sem leads gold) exibe toast informativo sem crash.
- [ ] Exportação disponível em `.xlsx` e `.csv`.
- [ ] CSV usa separador `;` e encoding UTF-8 com BOM.

---

## 5. Fora de Escopo (neste ciclo)

- Exportação de leads em outros estágios (`bronze`, `silver`)
- Envio do arquivo por e-mail
- Agendamento automático de exportações
- Integração com ferramentas externas (Google Sheets, CRMs)
- Edição em massa de leads via exportação/reimportação

---

## 6. Dependências Técnicas

| Item | Dependência | Risco |
|---|---|---|
| 3.1 — Data padrão | Apenas frontend | Baixo |
| 3.2 — Data no dropdown | Backend: estender `GET /leads/referencias/eventos` | Baixo |
| 3.3 — Campos removidos | Levantar schema do banco de dados anterior; migration | Médio-alto |
| 3.4 — Criação rápida de evento | `POST /evento/` já funcional; apenas frontend | Baixo |
| 4 — Exportação Gold | Novo endpoint `GET /leads/export/gold`; novo serviço frontend | Médio |
| 4 (colunas extras) | Depende de 3.3 para campos como `genero`, `rg`, endereço | Médio |

---

## 7. Perguntas em Aberto

- [ ] **3.3** — O banco atual tem colunas `sobrenome`, `rg`, `genero` e endereço? Ou foram removidas em alguma migration? Confirmar com DBA/backend.
- [ ] **3.3** — O campo `nome` atual armazena nome completo ou apenas primeiro nome? Se completo, `sobrenome` pode ser derivado.
- [ ] **3.4** — No modal de criação rápida, `diretoria_id` é obrigatório na API (`POST /evento/`). O smoke test usa `DIPES` como fallback — confirmar se há uma diretoria padrão para o caso de uso de marketing.
- [ ] **4.5** — O endpoint de exportação deve ser novo (`/leads/export/gold`) ou reutilizar algum existente via parâmetro `stage`?
- [ ] **4.9** — Leads com `pipeline_status = "pass_with_warnings"` devem entrar na exportação? (Proposta: sim, mas com coluna indicativa de aviso.)
- [ ] **Permissões** — Quais roles podem acessar a exportação? Todos os usuários autenticados ou apenas `npbb_reviewer` / admin?
