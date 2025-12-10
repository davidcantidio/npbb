# Configuração do Formulário de Lead e Página de Captura

## 1. Nome da Tela
**Configuração de Formulário de Lead / Landing Page**

Segunda etapa do cadastro/edição de evento.  
Usada para configurar:

- aparência da página de captura (landing)  
- campos do formulário de lead  
- geração de URLs para:
  - landing (cadastro inicial na ativação/ação)
  - questionário de feedback
  - página para promotor (lead de campo)

---

## 2. Referência Visual
Print (sistema original):  
`C:\Users\NPBB\OneDrive - Banco do Brasil S.A\Documentos\code\npbb\docs\tela-inicial\menu\Eventos\Novo evento\form_formulario_leads\form_formulario_leads.png` *(ajustar caminho real depois)*

Estado exibido: formulário de configuração já preenchido, com tema selecionado e campos marcados.

---

## 3. Estrutura da Tela (Componentes Visíveis)

### 3.1 Navegação / Contexto
- Abas do evento:
  - Evento
  - **Formulário de Lead** (aba atual)
  - Gamificação
  - Ingressos / Cotas
  - Ativações
  - Questionário
- Título da seção: algo como “Configuração do Formulário / Landing”

---

### 3.2 Seção: Temas (Layout da Página de Captura)

- Lista de **temas visuais** (cards ou radio buttons) representando estilos de página:
  - Cada tema mostra uma miniatura pré-visualizando o layout
  - Apenas um tema pode ser selecionado por vez
- Campo selecionado alimenta um atributo do evento (ex.: `form_theme` ou similar)

**Na prática:**  
> “Temas” = **estilos de página gerada**. Ao selecionar um tema, a página de captura (landing) é renderizada usando aquele layout.

---

### 3.3 Seção: Campos do Formulário

Lista de campos possíveis para o formulário de lead, com **checkbox** para incluir/excluir cada campo:

Prováveis campos (baseado no que já definimos no modelo `lead`):

- Nome  
- Sobrenome  
- CPF  
- Email  
- Telefone  
- Data de nascimento  
- Aceite de termos (se existir no original)  
- Campos extras opcionais (ex.: cidade, cargo, etc. – conforme original)

Comportamento:

- Marcar/desmarcar define quais campos aparecerão na página de captura daquele evento
- Alguns campos podem ser obrigatórios por regra de negócio (ex.: CPF, nome, data de nascimento)

---

### 3.4 Seção: URLs Geradas

Na parte inferior da tela são exibidas **URLs geradas automaticamente** após configuração:

1. **Endereço da Landing**
   - URL da página de captura inicial para o lead
   - Usada na ativação/ação como página principal de cadastro
   - Ex.: `https://.../landing/{token_evento_ou_form}`

2. **Endereço do Questionário**
   - URL da página de **questionário de feedback da ação**
   - Lead acessa após a ativação, para medir satisfação
   - Ex.: `https://.../questionario/{token_evento_ou_lead}`

3. **Endereço para Promotor**
   - URL especial para uso por **promotor em campo**
   - Função provável:
     - permitir que promotores cadastrem novos leads ligados a ativações específicas
   - Papel no nosso sistema:
     - registrar leads operacionais “de campo” vinculados a evento/ativação
   - **Ponto em aberto:** comportamento exato ainda deve ser validado no sistema original.

---

## 4. Comportamento da Tela

- Ao selecionar um **tema**, o sistema:
  - marca visualmente o tema
  - salva a referência para uso na renderização da landing

- Ao marcar/desmarcar **campos do formulário**:
  - atualiza a configuração dos campos que irão compor o formulário de lead
  - alguns campos podem ser sempre obrigatórios (ex.: CPF)

- Ao confirmar/salvar:
  - o backend registra:
    - tema selecionado
    - lista de campos ativos
    - gera (ou atualiza) as URLs:
      - landing
      - questionário
      - promotor

- URLs são exibidas como texto copiável (link ou botão “copiar”).

---

## 5. Regras de Negócio Identificadas

- Cada **evento** tem sua própria configuração de:
  - tema de página
  - campos do formulário
  - URLs de acesso

- Campos mínimos para lead no nosso sistema (base de dados) são:
  - Nome
  - Sobrenome
  - CPF
  - Data de nascimento
  - (Email/telefone podem ser configuráveis, mas são desejáveis)

- Formulário configurado aqui alimenta:
  - criação de lead no Salesforce
  - criação de lead no nosso banco (`lead` + `salesforce_id`)

- **Landing**:
  - É a página padrão de cadastro do lead
  - Associada ao evento (e possivelmente à ativação, dependendo de como a URL for usada)

- **Questionário**:
  - É a página de pesquisa de satisfação
  - Deve estar ligada ao evento
  - Pode ser acessada após a participação na ação

- **URL do promotor**:
  - Ligada ao evento (e provavelmente à ativação)
  - Usada por profissionais em campo
  - Deve registrar lead da mesma forma, só que com origem “promotor”

---

## 6. Diferenças Entre o Original e a Nossa Versão

### Original:
- Temas definidos para landing  
- Seleção de campos  
- Geração de múltiplas URLs para:
  - landing  
  - questionário  
  - promotor  

### Nossa Versão:
- Mantém:
  - seleção de tema  
  - seleção de campos  
  - geração de URLs  
- Adapta:
  - Persistência dos dados de configuração em tabelas próprias (ex.: `form_config`, `form_field_config` ou campos adicionais em `evento`)
  - Integração com Salesforce via backend FastAPI
  - Sem tela de módulo “Leads” no menu — lead é consequência dessa configuração, não módulo isolado

---

## 7. Pendências / Pontos a Confirmar

- Comportamento exato da **URL do promotor**:
  - confirma se:
    - promotor escolhe a ativação antes de cadastrar lead, OU
    - a URL já “encapsula” evento + ativação

- Precisamos decidir:
  - se haverá personalização de textos (título, descrição, mensagem de agradecimento) por formulário
  - se a landing poderá ter campos extras além dos que existem hoje

- Relacionamento exato do questionário:
  - por evento?
  - por ativação?
  - por lead?

---

## 8. Desdobramento em Requisitos (Backlog da Tela)

### Backend (FastAPI)
- Endpoint `GET /eventos/{id}/form-config`
- Endpoint `PUT /eventos/{id}/form-config`
  - Recebe:
    - tema selecionado
    - lista de campos ativos
  - Gera/atualiza:
    - URL landing
    - URL questionário
    - URL promotor

- Definir modelo de dados:
  - tabela/configuração de tema por evento
  - tabela/configuração de campos por evento
  - armazenamento das URLs (slug/token)

### Frontend (React)
- Aba `<EventoFormLead />`
- Componentes:
  - Lista de temas (cards/radios)
  - Lista de campos (checkbox)
  - Seção de URLs (com botão “copiar”)
- Lógica:
  - Carregar config ao abrir a aba
  - Enviar mudanças ao salvar
  - Mostrar feedback de sucesso/erro

---

