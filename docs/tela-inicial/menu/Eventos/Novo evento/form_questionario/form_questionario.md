# Aba de QuestionÃ¡rio (Cadastro / EdiÃ§Ã£o)

## 1. Nome da Tela
**QuestionÃ¡rio de SatisfaÃ§Ã£o**  
Tela usada para configurar o **questionÃ¡rio de feedback** respondido pelo lead apÃ³s a participaÃ§Ã£o na aÃ§Ã£o/ativaÃ§Ã£o.  
Permite criar **pÃ¡ginas** de questionÃ¡rio e, dentro delas, mÃºltiplas **perguntas** de tipos variados.

---

## 2. ReferÃªncia Visual
Prints da tela (sistema original):  
- `docs/tela-inicial/menu/Eventos/Editar/questionario_1.png`  
- `docs/tela-inicial/menu/Eventos/Editar/questionario_2.png`  

Estados exibidos:
- CriaÃ§Ã£o da PÃ¡gina 1, com tÃ­tulo, descriÃ§Ã£o e menu â€œIncluir perguntaâ€.  
- QuestionÃ¡rio com mÃºltiplas pÃ¡ginas (PÃ¡gina 1, PÃ¡gina 2) e estrutura listada Ã  direita.

---

## 3. Estrutura da Tela (Componentes VisÃ­veis)

### 3.1 NavegaÃ§Ã£o
- Menu lateral:
  - Dashboard  
  - Leads *(serÃ¡ removido no nosso sistema)*  
  - Eventos  
  - Cupons  
- Logo Banco do Brasil

### 3.2 Header Superior
- Ãcone menu sanduÃ­che  
- Ãcone fullscreen  
- Ãcone modo escuro  
- Perfil do usuÃ¡rio (Admin)  
- Breadcrumb: `Dashboard > Eventos > Editar`

### 3.3 Guias Superiores (Abas do Evento)

| Ordem | Aba               | Status no Novo Sistema |
|-------|-------------------|-------------------------|
| 1     | Evento            | Mantida                |
| 2     | FormulÃ¡rio de Lead| Mantida                |
| 3     | Ingressos / Cotas | **Nova** (substitui GamificaÃ§Ã£o) |
| 4     | AtivaÃ§Ãµes         | Mantida                |
| 5     | **QuestionÃ¡rio**  | Aba atual              |

---

### 3.4 ConteÃºdo da Aba â€œQuestionÃ¡rioâ€

A aba Ã© organizada em **pÃ¡ginas** de questionÃ¡rio, cada uma com tÃ­tulo, descriÃ§Ã£o e perguntas.

#### 3.4.1 Bloco de PÃ¡gina (ex.: PÃ¡gina 1, PÃ¡gina 2, ...)

Para cada pÃ¡gina, sÃ£o exibidos:

| #  | Campo / Elemento        | Tipo / Componente             | ObservaÃ§Ã£o |
|----|-------------------------|-------------------------------|-----------|
| 1  | RÃ³tulo â€œPÃ¡gina Xâ€       | Texto (header da seÃ§Ã£o)      | X = nÃºmero da pÃ¡gina |
| 2  | TÃ­tulo da pÃ¡gina \*     | Campo texto                  | ObrigatÃ³rio |
| 3  | DescriÃ§Ã£o da pÃ¡gina     | Textarea                     | Opcional |
| 4  | BotÃ£o â€œIncluir perguntaâ€| Dropdown de tipos de pergunta| Abre lista de tipos |
| 5  | BotÃ£o â€œExcluir pÃ¡ginaâ€  | Ãcone lixeira (topo da pÃ¡gina)| Remove pÃ¡gina |
| 6  | Setas de ordenaÃ§Ã£o      | Ãcone â€œmover para cima/baixoâ€| Reordenar pÃ¡ginas (print 2) |
| 7  | BotÃ£o â€œAdicionar pÃ¡ginaâ€| BotÃ£o ao final da Ãºltima pÃ¡gina| Cria nova pÃ¡gina |

#### 3.4.2 Tipos de Pergunta

Ao clicar em **â€œIncluir perguntaâ€**, aparece um dropdown com os tipos:

- Aberta texto simples  
- Aberta Ã¡rea de texto  
- Objetiva Ãºnica escolha  
- Objetiva mÃºltipla escolha  
- Data  
- AvaliaÃ§Ã£o  
- NumÃ©rica  

Cada seleÃ§Ã£o cria um bloco de pergunta (nÃ£o aparece detalhado nos prints, mas o comportamento Ã© tÃ­pico: enunciado + opÃ§Ãµes quando aplicÃ¡vel).

#### 3.4.3 Estrutura (Painel Ã  direita)

- Caixa â€œEstruturaâ€ lista as pÃ¡ginas do questionÃ¡rio:
  - Ex.:  
    - `1 - nova pÃ¡gina de questionÃ¡rio de satisfaÃ§Ã£o`  
    - `2 - ...`  
- Serve como **mapa do questionÃ¡rio**, exibindo tÃ­tulo da pÃ¡gina e ordem.

#### 3.4.4 RodapÃ©

- BotÃ£o **Salvar** (inferior direito) para persistir toda a estrutura do questionÃ¡rio.
- Abaixo (jÃ¡ na mesma tela) aparecem as seÃ§Ãµes de URLs (landing, promotor, questionÃ¡rio), mapeadas em outro documento.

---

## 4. Comportamento da Tela

- **Criar pÃ¡gina**:  
  - Clicar em â€œAdicionar pÃ¡ginaâ€ cria nova pÃ¡gina vazia (PÃ¡gina 2, 3, ...).
  - O painel de Estrutura Ã© atualizado.

- **Editar pÃ¡gina**:  
  - Alterar tÃ­tulo / descriÃ§Ã£o atualiza os dados da pÃ¡gina.
  - O tÃ­tulo exibido no painel Estrutura tambÃ©m Ã© atualizado.

- **Reordenar pÃ¡ginas**:  
  - Setas de mover (cima/baixo) alteram a ordem das pÃ¡ginas.
  - A ordem refletida na Estrutura muda (1, 2, 3, ...).

- **Excluir pÃ¡gina**:  
  - Ãcone de lixeira remove a pÃ¡gina e todas suas perguntas.
  - Reordena numeraÃ§Ã£o das pÃ¡ginas restantes.

- **Adicionar pergunta**:  
  - Ao selecionar um tipo no dropdown, Ã© incluÃ­da uma pergunta na pÃ¡gina atual.
  - Pergunta provavelmente contÃ©m: enunciado, obrigatoriedade, opÃ§Ãµes (para objetivas/avaliaÃ§Ã£o).

- **Salvar**:  
  - BotÃ£o â€œSalvarâ€ persiste todas as pÃ¡ginas, perguntas e opÃ§Ãµes.
  - Exibe toast â€œDados atualizados.â€ (como na imagem).

---

## 5. Regras de NegÃ³cio Principais

| Regra | Detalhe |
|-------|---------|
| QuestionÃ¡rio associado ao evento | A configuraÃ§Ã£o pertence ao evento (e Ã© usada para avaliar satisfaÃ§Ã£o das aÃ§Ãµes/ativaÃ§Ãµes deste evento). |
| PÃ¡gina necessita de tÃ­tulo | Campo obrigatÃ³rio. |
| Ordem das pÃ¡ginas importa | NavegaÃ§Ã£o do questionÃ¡rio segue a ordem configurada. |
| Tipos de pergunta prÃ©-definidos | Somente os tipos listados podem ser usados. |
| Perguntas objetivas | Devem ter opÃ§Ãµes associadas (checkbox/radio). |
| QuestionÃ¡rio de satisfaÃ§Ã£o | Respostas nÃ£o estÃ£o modeladas ainda (fora do escopo inicial). |

> ObservaÃ§Ã£o: apesar da satisfaÃ§Ã£o estar ligada Ã  **aÃ§Ã£o/ativaÃ§Ã£o**, no sistema original a UI estÃ¡ no nÃ­vel do **evento**. No nosso modelo, questionÃ¡rio Ã© configurado por evento e poderÃ¡ ser utilizado como questionÃ¡rio padrÃ£o de satisfaÃ§Ã£o das ativaÃ§Ãµes daquele evento.

---

## 6. DiferenÃ§as â€“ Sistema Original Ã— Nova VersÃ£o

| Item                          | Sistema Original                           | Nova VersÃ£o |
|-------------------------------|--------------------------------------------|------------|
| AssociaÃ§Ã£o                    | QuestionÃ¡rio cadastrado por evento         | Mantemos este modelo (1 questionÃ¡rio configurÃ¡vel por evento, podendo avaliar ativaÃ§Ãµes) |
| EdiÃ§Ã£o de perguntas           | Interface visual com pÃ¡ginas e tipos       | Mantida com Material Design 3 |
| Armazenamento                 | NÃ£o modelado (caixa preta)                 | Modelagem explÃ­cita em tabelas de pÃ¡gina, pergunta e opÃ§Ã£o |
| Respostas de questionÃ¡rio     | NÃ£o visÃ­vel                                | MVP: foco sÃ³ em configuraÃ§Ã£o; respostas podem ser fase futura |

---

## 7. Modelo de Banco de Dados (ConfiguraÃ§Ã£o do QuestionÃ¡rio)

> **Objetivo aqui:** armazenar a **estrutura do questionÃ¡rio** (pÃ¡ginas, perguntas, opÃ§Ãµes).  
> Respostas de usuÃ¡rios podem ser modeladas numa etapa futura.

### 7.1 Tabela `questionario_pagina`

> Inserir **apÃ³s a tabela `ativacao` / `gamificacao`**, pois depende de `evento`.

```sql
CREATE TABLE questionario_pagina (
    id SERIAL PRIMARY KEY,
    evento_id INT NOT NULL,
    ordem INT NOT NULL,                 -- posiÃ§Ã£o da pÃ¡gina (1, 2, 3...)
    titulo VARCHAR(200) NOT NULL,
    descricao TEXT,

    FOREIGN KEY (evento_id) REFERENCES evento(id),
    UNIQUE (evento_id, ordem)          -- cada ordem Ãºnica por evento
);

Backlog da Tela (Requisitos)
Backend

Endpoints:

GET /eventos/{id}/questionario (carregar estrutura completa)

PUT /eventos/{id}/questionario (salvar pÃ¡ginas + perguntas + opÃ§Ãµes)

OperaÃ§Ãµes:

Criar/editar/excluir pÃ¡ginas

Criar/editar/excluir perguntas

Criar/editar/excluir opÃ§Ãµes

Manter ordens (pÃ¡ginas / perguntas / opÃ§Ãµes)

Frontend

Componente <QuestionarioEditor /> com:

Blocos de pÃ¡gina (reordenÃ¡veis)

BotÃ£o â€œAdicionar pÃ¡ginaâ€

BotÃ£o â€œIncluir perguntaâ€

Modal ou inline editor para perguntas e opÃ§Ãµes

Painel â€œEstruturaâ€ Ã  direita

ValidaÃ§Ã£o de:

TÃ­tulo da pÃ¡gina obrigatÃ³rio

Pelo menos uma pergunta para questionÃ¡rio ser considerado â€œativoâ€ (regra opcional)

IntegraÃ§Ã£o com botÃ£o â€œSalvarâ€ e feedback visual (â€œDados atualizadosâ€).
