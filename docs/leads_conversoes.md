# Conversoes de Lead (PRD curto)

## 1. Objetivo
Registrar **todas as conversoes** de um lead ao longo do tempo, permitindo:
- Diferenciar conversao por **compra de ingresso** vs **acao em evento**.
- Contabilizar **quantas vezes** o mesmo lead converteu.
- Auditar **tipo**, **acao** e **evento** associados a cada conversao.

## 2. Modelo de dados
Entidade: **LeadConversao**

Campos:
- `id` (PK)
- `lead_id` (FK -> lead.id)
- `tipo` (enum): `COMPRA_INGRESSO` | `ACAO_EVENTO`
- `acao_nome` (string, opcional) — **obrigatorio** quando `tipo=ACAO_EVENTO`
- `fonte_origem` (string, opcional) — ex.: `EVENTIM`
- `evento_id` (FK -> evento.id, opcional)
- `data_conversao_evento` (datetime, opcional) — data/hora especifica durante o evento
- `created_at` (datetime)

Relacionamento:
- **Lead 1:N LeadConversao**

## 3. Regras de validacao
- Se `tipo=ACAO_EVENTO` -> `acao_nome` **obrigatorio**.
- Se `tipo=COMPRA_INGRESSO` -> `acao_nome` **deve ser nulo**.

## 4. Origem das conversoes
### 4.1 Compra de ingresso (ticketing)
- Conversao gerada automaticamente na importacao de dados de ticketeiras.
- Ex.: Eventim -> cria `LeadConversao` com `tipo=COMPRA_INGRESSO`, `fonte_origem=EVENTIM`, `evento_id` quando resolvido.

### 4.2 Acao em evento (ativacao)
- Conversao registrada quando o lead executa uma acao especifica (ex.: check-in, quiz, ativacao X).
- `acao_nome` identifica o tipo da acao (ex.: "checkin", "quiz", "ativacao:brinde").

## 5. API (basico)
- `POST /leads/{lead_id}/conversoes`
- `GET /leads/{lead_id}/conversoes`
- `GET /leads?page=&page_size=` (listagem paginada com a conversao mais recente por lead)

## 6. Uso esperado
Relatorios e analises devem considerar:
- **Quantidade de conversoes por lead**.
- **Mix por tipo** (compra vs acao).
- **Distribuicao por evento**.

## 7. Fluxo de importacao de Leads (pagina Leads)
### 7.1 Entrada
- Botao **Importar leads**.
- Abre seletor de arquivo (CSV/planilha).
 - Suporte a **CSV e XLSX** no preview/import.

### 7.2 Detecao automatica
- Sistema identifica:
  - **Linha de inicio dos dados** (pula cabecalhos/linhas soltas).
  - Possiveis **colunas reconheciveis** (email, CPF, datas, numeros).
- Campos reconheciveis aparecem **pre-selecionados** (usuario confirma).

### 7.3 Mapeamento assistido
- Usuario mapeia **coluna da planilha** -> **campo do banco** via dropdown.
- Se a planilha tiver **cabecalhos agregados/omissos**, o mapeamento pode ser feito:
  - Pela **amostra de dados** (valores da coluna), e nao pelo nome do cabecalho.
- Cada coluna pode ser marcada como:
  - **Ignorar**
  - **Mapear para campo existente**
- **Confianca**: exibida como *sugestao*, nunca como verdade absoluta. Deve evitar 100% quando houver ambiguidade ou baixa amostra.

### 7.3.1 Campos com correspondencia por alias (nome/cidade/estado/genero)
- Campos: **Nome do evento**, **Cidade**, **Estado**, **Genero**.
- Ao mapear um valor para um campo de referencia (ex.: Nome do evento), a UI deve abrir
  um **dropdown secundario** com as opcoes existentes no banco.
- Se o valor da planilha **combina exatamente** com o registro do banco, o dropdown vem **pre-selecionado**.
- Se nao combinar exatamente, o sistema tenta:
  - **Correspondencia por similaridade** (fuzzy match, ex.: distancia de Levenshtein).
  - **Remocao de acentos e normalizacao** (maiusculas/minusculas, espacos).
- Em ultimo caso, o usuario seleciona manualmente o valor correto.

### 7.3.2 Aliases persistidos
- Quando o usuario confirma o valor correto para um campo de referencia,
  o texto original da planilha passa a ser salvo como **alias** daquele registro.
- Em importacoes futuras, o alias deve ser reconhecido automaticamente.
- Campos suportados: **Nome do evento**, **Cidade**, **Estado**, **Genero**.

### 7.3.3 DateTime com separacao de data/hora
- Se a coluna chegar como **data + hora**, o sistema deve:
  - **Detectar o formato** (ex.: `DD/MM/YYYY HH:mm` ou `YYYY-MM-DD HH:mm:ss`).
  - **Separar em data e hora**, armazenando em colunas distintas quando aplicavel.
- Decisao default:
  - Data vai para o campo principal (ex.: `data_compra` -> data).
  - Hora vai para um campo de apoio (ex.: `hora_compra`) quando existir no schema.

### 7.4 Confirmacao e importacao
- Usuario confirma o mapeamento.
- Sistema executa a importacao:
  - Normaliza formatos (email/CPF/datas/telefone).
  - Registra **fonte_origem** (ex.: EVENTIM).
  - Aplica deduplicacao definida.

### 7.5 Feedback
- Exibir resumo:
  - total de linhas
  - criados
  - atualizados
  - ignorados

### 7.6 Regras importantes
- Mapeamento **obrigatorio** para campos essenciais (email ou CPF).
- Campos opcionais podem ficar vazios.
- Dados incompletos nao bloqueiam o import (quando possivel).

## 8. UX/visual (importacao)
- Interface deve permitir **ignorar** colunas sem correspondencia.
- Mensagens de confianca devem ser **conservadoras** (evitar 100% quando houver risco de erro).
- Visual deve ser **mais leve e organizado** (grid/colunas, espaçamento consistente, destaque claro para o dropdown ativo).
