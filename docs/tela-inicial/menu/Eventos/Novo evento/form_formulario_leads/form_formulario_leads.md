# Configuração do Formulário de Lead / Landing Page

## 1. Nome da Tela
**Formulário de Lead** (aba do fluxo de novo evento/edição)

---

## 2. Referência Visual
Baseada na tela atual (tema + preview + checkboxes de campos + URLs e botões “Salvar e Visualizar” / “Salvar”).

---

## 3. Estrutura da Tela (Componentes Visíveis)

### 3.1 Navegação / Contexto
- Abas do evento:
  - Evento
  - **Formulário de Lead** (aba atual)
  - Gamificação
  - Ativações
  - Questionário
  - Ingressos/Cotas (rota dedicada)
  - Investimentos (rota dedicada)

### 3.2 Seção: Temas (Layout da Página de Captura)
- Temas disponíveis: Surf, Padrão, BB Seguros.
- Miniatura/preview do formulário exibida ao lado.
- Seleção única (radio/button).

### 3.3 Seção: Campos do Formulário
- Checkboxes (observado): CPF, Nome, Sobrenome, Telefone, E-mail, Data de Nascimento, Endereço, Interesses, Gênero, Área de atuação.
- Campos obrigatórios destacados; ordem configurável.

### 3.4 Seção: URLs Geradas
- Endereço da landing
- Endereço para promotor
- Endereço do questionário
- Endereço da API (com botão “Acessar documentação”)
- Botões “Visualizar” em cada linha.

### 3.5 Ações
- Botões: **Salvar e Visualizar**, **Salvar** (aplica config e permite pré-visualização).

---

## 4. Comportamento da Tela
- Seleção de tema atualiza preview.
- Checkboxes ligam/desligam campos do formulário; alguns são obrigatórios.
- Ao salvar, backend persiste tema, campos e URLs; permite pré-visualizar com “Salvar e Visualizar”.
- URLs exibidas com botões de acesso direto e link de documentação para API.

---

## 5. Regras de Negócio Identificadas
- Cada evento tem sua própria configuração de tema, campos e URLs.
- Campos mínimos para lead: Nome, Sobrenome, CPF, Data de nascimento (Email/Telefone desejáveis).
- Formulário alimenta: criação de lead no Salesforce + banco local (`lead` + `salesforce_id`).
- Landing associada ao evento; questionário associado ao evento; URL do promotor para cadastro em campo (provável vínculo a ativação ou token de evento).

---

## 6. Diferenças Entre o Original e a Nossa Versão
- Mantém: seleção de tema, seleção de campos, geração de URLs.
- Adapta: persistência em tabelas próprias (template HTML/CSS, configuração por evento, campos por evento, URLs).
- Integração com Salesforce via backend; sem módulo “Leads” no menu (lead é consequência desta configuração).

---

## 7. Pendências / Pontos a Confirmar
- Comportamento exato da URL do promotor (seleciona ativação ou token direto).
- Personalização de textos (título, descrição, mensagem de agradecimento) por formulário.
- Relacionamento do questionário (por evento/ativação/lead).

---

## 8. Desdobramento em Requisitos (Backlog da Tela)

### Backend (FastAPI)
- `GET /eventos/{id}/form-config`, `PUT /eventos/{id}/form-config`
  - Tema selecionado, lista de campos ativos
  - Geração/atualização das URLs: landing, questionário, promotor, API
- Modelo de dados: tabelas de template (HTML/CSS), config por evento, campos por evento, armazenamento das URLs (slug/token)

### Frontend (React)
- Aba `<EventoFormLead />`
- Componentes:
  - Lista de temas (cards/radios) + preview
  - Lista de campos (checkbox)
  - Seção de URLs (com botões “Visualizar” e link de documentação)
- Lógica:
  - Carregar config ao abrir a aba
  - Enviar mudanças ao salvar
  - Mostrar feedback de sucesso/erro
