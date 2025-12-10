# Aba de Ativações (Cadastro / Edição)

## 1. Nome da Tela
**Ativações do Evento**  
Tela usada para criar, editar e visualizar ativações pertencentes a um evento.  
Também permite configurar regras de gamificação e a mensagem do QR Code.

---

## 2. Referência Visual
Print da tela (sistema original):  
`docs/tela-inicial/menu/Eventos/Editar/ativacoes.png`

Estado exibido: formulário de cadastro de ativação e listagem de ativações já adicionadas.

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

---

### 3.3 Guias Superiores (Abas do Evento)

| Ordem | Aba                    | Status no Novo Sistema |
|-------|-------------------------|-------------------------|
| 1     | Evento                 | Mantida                |
| 2     | Formulário de Lead     | Mantida                |
| 3     | Gamificação            | **Será substituída por Ingressos / Cotas** |
| 4     | **Ativações**          | Aba atual              |
| 5     | Questionário           | Em avaliação           |

---

### 3.4 Conteúdo da Aba “Ativações”

#### Ordem dos campos (lado esquerdo)

| #  | Campo                                 | Tipo                          | Mapeamento no Banco                         | Observação |
|----|---------------------------------------|-------------------------------|----------------------------------------------|------------|
| 1  | Nome da ativação \*                   | Texto                         | `ativacao.nome`                              | Obrigatório |
| 2  | Mensagem do QR Code                   | Textarea (máx. 240 chars)     | `ativacao.mensagem_qrcode`                   | Exibida na tela do QR |
| 3  | Tipo de gamificação                   | Dropdown                      | **Não persiste diretamente**                 | Categoria visual |
| 4  | Redirecionamento para tela de pesquisa| Switch booleano               | `ativacao.redireciona_pesquisa`              |            |
| 5  | Check-in único por ativação           | Switch booleano               | `ativacao.checkin_unico`                     | Define “Único = Sim” |
| 6  | Termo de uso                          | Switch booleano               | `ativacao.termo_uso`                         |            |
| 7  | Gerar Cupom                           | Switch booleano               | `ativacao.gera_cupom`                        | Liga módulo de cupons |
| 8  | Botão “Adicionar ativação”            | Ação                          | —                                            | Cria ativação |

---

### 3.5 Lista de Ativações (lado direito)

Colunas exibidas:

| Coluna         | Descrição |
|----------------|-----------|
| **Nome**       | Nome da ativação cadastrada |
| **Único**      | “Sim” se `checkin_unico = TRUE` |
| **Gamificação**| “Sim” se qualquer switch de gamificação estiver habilitado |
| **Ações**      | Ver (azul), Editar (verde), Excluir (vermelho) |

---

## 4. Comportamento da Tela

### 4.1 Adicionar ativação
- Valida campos obrigatórios  
- Cria registro em `ativacao`  
- Salva switches como booleans diretos  
- Caso sejam necessários textos de gamificação (nome, descrição, prêmios), cria registro em `gamificacao` (1:1)  
- Atualiza tabela da direita

### 4.2 Editar ativação
- Botão verde preenche novamente o formulário  
- Alterações refletem direto no banco  
- Se switches forem desmarcados → gamificação pode ser removida

### 4.3 Excluir ativação
- Remove ativação  
- Remove gamificação associada (ON DELETE CASCADE)  
- Pode exigir bloqueio caso existam leads conectados (regra futura)

### 4.4 Lógica do campo “Único”
- Derivado exclusivamente de `checkin_unico`  
- Controla se um lead pode registrar apenas 1 interação naquela ativação

---

## 5. Regras de Negócio Principais

| Regra | Detalhe |
|-------|---------|
| Uma ativação pertence a um único evento | FK `evento_id` |
| Ativação pode ter 0 ou mais mecânicas de gamificação | Representadas como switches |
| Gamificação detalhada existe em tabela separada | `gamificacao` (1:1 com ativacao) |
| Check-in único | Impede múltiplos registros por lead |
| Gerar Cupom | Integra com módulo de cupons |
| Mensagem QR | Exibida na renderização do QR code da ativação |

---

## 6. Diferenças – Sistema Original × Nova Versão

| Item                     | Sistema Original                 | Nova Versão                      |
|--------------------------|----------------------------------|----------------------------------|
| Switches de gamificação | Independentes                    | Modelados como booleanos         |
| Tipo de gamificação      | Dropdown pouco funcional         | Mantido apenas como referência   |
| Banco de dados           | Indefinido                       | Estrutura clara: ativação + gamificação 1:1 |
| QR Code                  | Parcialmente documentado         | Mapeado em `mensagem_qrcode`     |
| Cupons                   | Usado apenas em gamificações     | Estrutura compatível para expansão |

---

## 7. Modelo de Banco de Dados

### 7.1 Tabela `ativacao` (versão final)

```sql
CREATE TABLE ativacao (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao VARCHAR(200) NOT NULL,
    evento_id INT NOT NULL,
    valor DECIMAL(12,2) NOT NULL,

    mensagem_qrcode VARCHAR(240),

    redireciona_pesquisa BOOLEAN DEFAULT FALSE,
    checkin_unico BOOLEAN DEFAULT FALSE,
    termo_uso BOOLEAN DEFAULT FALSE,
    gera_cupom BOOLEAN DEFAULT FALSE,

    FOREIGN KEY (evento_id) REFERENCES evento(id)
);
