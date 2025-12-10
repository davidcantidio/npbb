# Aba de Questionário (Cadastro / Edição)

## 1. Nome da Tela
**Questionário de Satisfação**  
Tela usada para configurar o **questionário de feedback** respondido pelo lead após a participação na ação/ativação.  
Permite criar **páginas** de questionário e, dentro delas, múltiplas **perguntas** de tipos variados.

---

## 2. Referência Visual
Prints da tela (sistema original):  
- `docs/tela-inicial/menu/Eventos/Editar/questionario_1.png`  
- `docs/tela-inicial/menu/Eventos/Editar/questionario_2.png`  

Estados exibidos:
- Criação da Página 1, com título, descrição e menu “Incluir pergunta”.  
- Questionário com múltiplas páginas (Página 1, Página 2) e estrutura listada à direita.

---

## 3. Estrutura da Tela (Componentes Visíveis)

### 3.1 Navegação
- Menu lateral:
  - Dashboard  
  - Leads *(será removido no nosso sistema)*  
  - Eventos  
  - Cupons  
- Logo Banco do Brasil

### 3.2 Header Superior
- Ícone menu sanduíche  
- Ícone fullscreen  
- Ícone modo escuro  
- Perfil do usuário (Admin)  
- Breadcrumb: `Dashboard > Eventos > Editar`

### 3.3 Guias Superiores (Abas do Evento)

| Ordem | Aba               | Status no Novo Sistema |
|-------|-------------------|-------------------------|
| 1     | Evento            | Mantida                |
| 2     | Formulário de Lead| Mantida                |
| 3     | Ingressos / Cotas | **Nova** (substitui Gamificação) |
| 4     | Ativações         | Mantida                |
| 5     | **Questionário**  | Aba atual              |

---

### 3.4 Conteúdo da Aba “Questionário”

A aba é organizada em **páginas** de questionário, cada uma com título, descrição e perguntas.

#### 3.4.1 Bloco de Página (ex.: Página 1, Página 2, ...)

Para cada página, são exibidos:

| #  | Campo / Elemento        | Tipo / Componente             | Observação |
|----|-------------------------|-------------------------------|-----------|
| 1  | Rótulo “Página X”       | Texto (header da seção)      | X = número da página |
| 2  | Título da página \*     | Campo texto                  | Obrigatório |
| 3  | Descrição da página     | Textarea                     | Opcional |
| 4  | Botão “Incluir pergunta”| Dropdown de tipos de pergunta| Abre lista de tipos |
| 5  | Botão “Excluir página”  | Ícone lixeira (topo da página)| Remove página |
| 6  | Setas de ordenação      | Ícone “mover para cima/baixo”| Reordenar páginas (print 2) |
| 7  | Botão “Adicionar página”| Botão ao final da última página| Cria nova página |

#### 3.4.2 Tipos de Pergunta

Ao clicar em **“Incluir pergunta”**, aparece um dropdown com os tipos:

- Aberta texto simples  
- Aberta área de texto  
- Objetiva única escolha  
- Objetiva múltipla escolha  
- Data  
- Avaliação  
- Numérica  

Cada seleção cria um bloco de pergunta (não aparece detalhado nos prints, mas o comportamento é típico: enunciado + opções quando aplicável).

#### 3.4.3 Estrutura (Painel à direita)

- Caixa “Estrutura” lista as páginas do questionário:
  - Ex.:  
    - `1 - nova página de questionário de satisfação`  
    - `2 - ...`  
- Serve como **mapa do questionário**, exibindo título da página e ordem.

#### 3.4.4 Rodapé

- Botão **Salvar** (inferior direito) para persistir toda a estrutura do questionário.
- Abaixo (já na mesma tela) aparecem as seções de URLs (landing, promotor, questionário), mapeadas em outro documento.

---

## 4. Comportamento da Tela

- **Criar página**:  
  - Clicar em “Adicionar página” cria nova página vazia (Página 2, 3, ...).
  - O painel de Estrutura é atualizado.

- **Editar página**:  
  - Alterar título / descrição atualiza os dados da página.
  - O título exibido no painel Estrutura também é atualizado.

- **Reordenar páginas**:  
  - Setas de mover (cima/baixo) alteram a ordem das páginas.
  - A ordem refletida na Estrutura muda (1, 2, 3, ...).

- **Excluir página**:  
  - Ícone de lixeira remove a página e todas suas perguntas.
  - Reordena numeração das páginas restantes.

- **Adicionar pergunta**:  
  - Ao selecionar um tipo no dropdown, é incluída uma pergunta na página atual.
  - Pergunta provavelmente contém: enunciado, obrigatoriedade, opções (para objetivas/avaliação).

- **Salvar**:  
  - Botão “Salvar” persiste todas as páginas, perguntas e opções.
  - Exibe toast “Dados atualizados.” (como na imagem).

---

## 5. Regras de Negócio Principais

| Regra | Detalhe |
|-------|---------|
| Questionário associado ao evento | A configuração pertence ao evento (e é usada para avaliar satisfação das ações/ativações deste evento). |
| Página necessita de título | Campo obrigatório. |
| Ordem das páginas importa | Navegação do questionário segue a ordem configurada. |
| Tipos de pergunta pré-definidos | Somente os tipos listados podem ser usados. |
| Perguntas objetivas | Devem ter opções associadas (checkbox/radio). |
| Questionário de satisfação | Respostas não estão modeladas ainda (fora do escopo inicial). |

> Observação: apesar da satisfação estar ligada à **ação/ativação**, no sistema original a UI está no nível do **evento**. No nosso modelo, questionário é configurado por evento e poderá ser utilizado como questionário padrão de satisfação das ativações daquele evento.

---

## 6. Diferenças – Sistema Original × Nova Versão

| Item                          | Sistema Original                           | Nova Versão |
|-------------------------------|--------------------------------------------|------------|
| Associação                    | Questionário cadastrado por evento         | Mantemos este modelo (1 questionário configurável por evento, podendo avaliar ativações) |
| Edição de perguntas           | Interface visual com páginas e tipos       | Mantida com Material Design 3 |
| Armazenamento                 | Não modelado (caixa preta)                 | Modelagem explícita em tabelas de página, pergunta e opção |
| Respostas de questionário     | Não visível                                | MVP: foco só em configuração; respostas podem ser fase futura |

---

## 7. Modelo de Banco de Dados (Configuração do Questionário)

> **Objetivo aqui:** armazenar a **estrutura do questionário** (páginas, perguntas, opções).  
> Respostas de usuários podem ser modeladas numa etapa futura.

### 7.1 Tabela `questionario_pagina`

> Inserir **após a tabela `ativacao` / `gamificacao`**, pois depende de `evento`.

```sql
CREATE TABLE questionario_pagina (
    id SERIAL PRIMARY KEY,
    evento_id INT NOT NULL,
    ordem INT NOT NULL,                 -- posição da página (1, 2, 3...)
    titulo VARCHAR(200) NOT NULL,
    descricao TEXT,

    FOREIGN KEY (evento_id) REFERENCES evento(id),
    UNIQUE (evento_id, ordem)          -- cada ordem única por evento
);

Backlog da Tela (Requisitos)
Backend

Endpoints:

GET /eventos/{id}/questionario (carregar estrutura completa)

PUT /eventos/{id}/questionario (salvar páginas + perguntas + opções)

Operações:

Criar/editar/excluir páginas

Criar/editar/excluir perguntas

Criar/editar/excluir opções

Manter ordens (páginas / perguntas / opções)

Frontend

Componente <QuestionarioEditor /> com:

Blocos de página (reordenáveis)

Botão “Adicionar página”

Botão “Incluir pergunta”

Modal ou inline editor para perguntas e opções

Painel “Estrutura” à direita

Validação de:

Título da página obrigatório

Pelo menos uma pergunta para questionário ser considerado “ativo” (regra opcional)

Integração com botão “Salvar” e feedback visual (“Dados atualizados”).
