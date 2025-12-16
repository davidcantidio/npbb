# Aba de Questionario (Evento)

## 1. Nome da Tela
**Questionario de Satisfacao** (configuracao)

Status no novo sistema:
- Frontend: nao implementado.
- Backend: nao implementado.

---

## 2. Objetivo
Permitir configurar um questionario de feedback por evento, com:
- paginas
- perguntas por pagina
- opcoes (quando aplicavel)
- ordenacao/reordenacao

O questionario seria respondido pelo lead ao final do fluxo (integracao e coleta de respostas ficam para uma fase futura).

---

## 3. Estrutura (proposta)
### 3.1 Paginas
Cada pagina possui:
- Titulo (obrigatorio)
- Descricao (opcional)
- Lista de perguntas

### 3.2 Perguntas
Tipos sugeridos:
- Texto curto
- Texto longo
- Unica escolha
- Multipla escolha
- Data
- Avaliacao
- Numerica

Para perguntas objetivas (unica/multipla escolha), a UI deve permitir cadastrar opcoes.

### 3.3 Painel "Estrutura"
Um painel lateral lista paginas e suas ordens para navegacao rapida e reordenacao.

---

## 4. Regras de negocio (proposta)
- Questionario pertence a um unico evento.
- Pagina precisa de titulo.
- Ordem das paginas e perguntas importa.
- Perguntas objetivas devem ter pelo menos 1 opcao.
- (Opcional) Validar que existe pelo menos 1 pergunta para considerar o questionario "ativo".

---

## 5. Modelo de dados (sugestao)
### Tabela `questionario_pagina`
- `id`
- `evento_id`
- `ordem`
- `titulo`
- `descricao`

### Tabela `questionario_pergunta`
- `id`
- `pagina_id`
- `ordem`
- `tipo`
- `enunciado`
- `obrigatoria`

### Tabela `questionario_opcao`
- `id`
- `pergunta_id`
- `ordem`
- `texto`

---

## 6. Endpoints (proposta / a confirmar)
Sugerido seguir o padrao do modulo de eventos (`/evento`):
- `GET /evento/{id}/questionario` (retorna estrutura completa)
- `PUT /evento/{id}/questionario` (salva estrutura completa)

Observacao: o PUT pode sobrescrever a estrutura inteira para simplificar (sem CRUD granular por item), ou pode existir CRUD separado por entidade (a definir).

---

## 7. Backlog (status)
### Backend
- [ ] Modelos/tabelas de questionario
- [ ] Endpoints para carregar/salvar estrutura
- [ ] Validacoes de tipos e obrigatorios

### Frontend
- [ ] Aba/pagina de questionario no detalhe do evento
- [ ] Editor de paginas/perguntas/opcoes com reordenacao
- [ ] Botao salvar + feedback de sucesso/erro
