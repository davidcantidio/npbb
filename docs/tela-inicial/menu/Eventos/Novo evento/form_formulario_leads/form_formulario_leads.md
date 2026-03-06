# Configuracao do Formulario de Lead / Landing Page (Evento)

## 1. Nome da Tela
**Formulario de Lead** (aba do evento)

Status no novo sistema:
- Frontend: implementado (tema + campos + URLs + preview operacional da landing + salvar).
- Backend: implementado (endpoints + templates + catalogo de campos).

---

## 2. Objetivo
Configurar a pagina de captura (landing) e os campos do formulario de lead por evento, incluindo:
- tema/layout
- campos ativos (checkbox)
- URLs geradas (landing, check-in sem QR, questionario)

---

## 3. Estrutura (proposta)
### 3.1 Temas e contexto da landing
- Lista de temas/templates suportados (ex.: `generico`, `corporativo`, `esporte_convencional`, `evento_cultural`, `tecnologia`).
- Selecao unica.
- `template_override` opcional para forcar categoria.
- `hero_image_url`, `cta_personalizado` e `descricao_curta` ajustam a experiencia publicada.

### 3.2 Campos do formulario
Checkboxes (exemplo observado no sistema original):
- CPF, Nome, Sobrenome, Telefone, Email, Data de nascimento, Endereco, Interesses, Genero, Area de atuacao

### 3.3 Preview operacional
- Painel embutido na propria tela de configuracao.
- Usa o mesmo contrato da landing publica (`GET /eventos/{id}/landing`).
- Exibe hero, CTA, categoria resolvida, blocos principais e checklist minimo de ativacao.

### 3.4 URLs geradas
- URL da landing
- URL para check-in sem QR
- URL do questionario
- URL da API (link para documentacao)

### 3.5 Acoes
- Botao **Salvar**
- Botao **Atualizar preview**
- Botao **Abrir landing publica**

---

## 4. Regras de negocio (proposta)
- Cada evento possui sua propria configuracao (tema + campos + URLs).
- Definir quais campos sao obrigatorios e quais sao opcionais.
- Integracao de envio do lead:
  - MVP: armazenar em banco local
  - Fase 2: integrar com Salesforce (se aplicavel)

### 4.1 Contrato de persistencia (MVP)
Decisao para representar "campos ativos" e "obrigatorio" no backend:
- "Campo ativo" = existe um registro em `FormularioLeadCampo` (tabela `formulario_lead_campo`) para a configuracao do evento (`config_id`).
  - Campo desativado = ausencia do registro.
- `obrigatorio` (bool) = se o campo deve ser obrigatorio no preenchimento do formulario.
- `ordem` (int) = ordem de exibicao (ordenacao ascendente) dos campos no formulario.

Observacao:
- A chave natural de um campo dentro de uma configuracao e `nome_campo`.
  - Boa pratica: nao permitir nomes duplicados por `config_id` (validar na API).

---

## 5. Endpoints (implementado)
Contrato detalhado: `docs/formulario_lead_api.md`

Padrao do modulo de eventos (`/evento`):
- `GET /evento/{id}/form-config`
- `PUT /evento/{id}/form-config`
- `GET /evento/all/formulario-templates`
- `GET /evento/all/formulario-campos` (opcional)

Observacao (MVP): as URLs (landing/check-in sem QR/questionario) sao geradas a partir de `evento.id`.

---

## 6. Backlog (status)
### Backend
- [x] Modelo/tabelas para templates e configuracao por evento (ja existem no backend)
- [x] Endpoints para ler/salvar configuracao
- [x] Estrategia de URLs (MVP por evento_id) + politica de acesso (AGENCIA ve apenas sua agencia)

### Frontend
- [x] Aba/pagina de formulario de lead no detalhe do evento
- [x] Selecao de tema + checkboxes + secao de URLs + salvar
- [x] Preview do template com checklist operacional, usando o contrato real da landing
