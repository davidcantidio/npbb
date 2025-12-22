# Configuracao do Formulario de Lead / Landing Page (Evento)

## 1. Nome da Tela
**Formulario de Lead** (aba do evento)

Status no novo sistema:
- Frontend: nao implementado.
- Backend: parcialmente implementado (modelos/migrations existem; endpoints pendentes).

---

## 2. Objetivo
Configurar a pagina de captura (landing) e os campos do formulario de lead por evento, incluindo:
- tema/layout
- campos ativos (checkbox)
- URLs geradas (landing, promotor, questionario)

---

## 3. Estrutura (proposta)
### 3.1 Temas
- Lista de temas (ex.: Surf, Padrao, BB Seguros).
- Selecao unica.
- Preview ao lado.

### 3.2 Campos do formulario
Checkboxes (exemplo observado no sistema original):
- CPF, Nome, Sobrenome, Telefone, Email, Data de nascimento, Endereco, Interesses, Genero, Area de atuacao

### 3.3 URLs geradas
- URL da landing
- URL para promotor
- URL do questionario
- URL da API (link para documentacao)

### 3.4 Acoes
- Botao **Salvar**
- Botao **Salvar e visualizar** (abre preview)

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

## 5. Endpoints (proposta / a confirmar)
Sugerido seguir o padrao do modulo de eventos (`/evento`):
- `GET /evento/{id}/form-config`
- `PUT /evento/{id}/form-config`

Observacao: as URLs (landing/promotor/questionario) podem ser geradas a partir de `evento.id` e/ou `slug/token` (a definir).

---

## 6. Backlog (status)
### Backend
- [x] Modelo/tabelas para templates e configuracao por evento (ja existem no backend)
- [ ] Endpoints para ler/salvar configuracao
- [ ] Definir estrategia de URLs (slug/token) e politica de acesso

### Frontend
- [ ] Aba/pagina de formulario de lead no detalhe do evento
- [ ] Selecao de tema + preview + checkboxes + secao de URLs
