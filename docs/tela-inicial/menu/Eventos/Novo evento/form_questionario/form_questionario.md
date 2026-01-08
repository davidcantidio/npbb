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
- `texto`
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

## 6.1 Contrato (MVP) - decisoes
### 6.1.1 JSON e nomes de campos
- Payload em `snake_case`.
- Campo da pergunta no payload: `texto` (alinhado ao modelo atual do backend).
- `id` aparece no GET e e opcional no PUT (read-only; pode ser usado em upsert no futuro).
- `opcao.valor_numerico` fica fora do MVP.

### 6.1.2 Tipos aceitos (campo `tipo`)
- `aberta_texto_simples`
- `aberta_texto_area`
- `objetiva_unica`
- `objetiva_multipla`
- `data`
- `avaliacao`
- `numerica`

### 6.2 Mapa de tipos (doc -> enum -> label UI)
| Doc (tipo sugerido) | Enum `TipoPergunta` | Label UI (sugerido) |
| --- | --- | --- |
| Texto curto | `aberta_texto_simples` | Texto curto |
| Texto longo | `aberta_texto_area` | Texto longo |
| Unica escolha | `objetiva_unica` | Unica escolha |
| Multipla escolha | `objetiva_multipla` | Multipla escolha |
| Data | `data` | Data |
| Avaliacao | `avaliacao` | Avaliacao |
| Numerica | `numerica` | Numerica |

### 6.3 Estrategia de persistencia (PUT)
- MVP: replace-all (delete + insert) por evento.
- Itens removidos do payload sao excluidos no banco.
- `id` no PUT e ignorado (read-only); novos ids sao gerados na persistencia.
- `ordem` e persistido conforme enviado (validacao definida na issue de ordenacao).
- Operacao deve ser transacional.

### 6.4 Regra de ordenacao (paginas/perguntas/opcoes)
- `ordem` e obrigatoria e deve ser inteiro >= 1.
- Para cada nivel:
  - paginas: `ordem` unica dentro do evento
  - perguntas: `ordem` unica dentro da pagina
  - opcoes: `ordem` unica dentro da pergunta
- O backend valida que a sequencia seja continua (1..N). Gaps, duplicados ou valores fora da faixa sao invalidos.
- Se invalido, retornar erro `QUESTIONARIO_INVALID_STRUCTURE`.

### 6.5 Validacoes MVP
- `pagina.titulo`: obrigatorio, trim, max 200.
- `pergunta.texto`: obrigatorio, trim, max 500.
- `pergunta.tipo`: obrigatorio (ver lista de tipos aceitos).
- `pergunta.obrigatoria`: default `false` quando ausente.
- Perguntas objetivas (`objetiva_unica`/`objetiva_multipla`) devem ter `opcoes` com pelo menos 1 item.
  - `opcao.texto`: obrigatorio, trim, max 200.
- Questionario vazio: permitido (pode salvar `paginas=[]`).

### 6.1.3 Exemplo de GET /evento/{id}/questionario
```json
{
  "evento_id": 123,
  "paginas": [
    {
      "id": 10,
      "ordem": 1,
      "titulo": "Pagina 1",
      "descricao": "Opcional",
      "perguntas": [
        {
          "id": 100,
          "ordem": 1,
          "tipo": "objetiva_unica",
          "texto": "Como voce avalia?",
          "obrigatoria": true,
          "opcoes": [
            { "id": 1000, "ordem": 1, "texto": "Otimo" },
            { "id": 1001, "ordem": 2, "texto": "Bom" }
          ]
        }
      ]
    }
  ]
}
```

### 6.1.4 Exemplo de PUT /evento/{id}/questionario
```json
{
  "paginas": [
    {
      "ordem": 1,
      "titulo": "Pagina 1",
      "descricao": "Opcional",
      "perguntas": [
        {
          "ordem": 1,
          "tipo": "aberta_texto_simples",
          "texto": "Deixe um comentario",
          "obrigatoria": false,
          "opcoes": []
        }
      ]
    }
  ]
}
```

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
