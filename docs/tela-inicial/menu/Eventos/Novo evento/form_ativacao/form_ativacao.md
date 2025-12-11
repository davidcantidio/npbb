# Aba de AtivaÃ§Ãµes (Cadastro / EdiÃ§Ã£o)

## 1. Nome da Tela
**AtivaÃ§Ãµes do Evento**  
Tela usada para criar, editar e visualizar ativaÃ§Ãµes pertencentes a um evento.  
TambÃ©m permite configurar regras de gamificaÃ§Ã£o e a mensagem do QR Code.

---

## 2. ReferÃªncia Visual
Print da tela (sistema original):  
`docs/tela-inicial/menu/Eventos/Editar/ativacoes.png`

Estado exibido: formulÃ¡rio de cadastro de ativaÃ§Ã£o e listagem de ativaÃ§Ãµes jÃ¡ adicionadas.

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

---

### 3.3 Guias Superiores (Abas do Evento)

| Ordem | Aba                    | Status no Novo Sistema |
|-------|-------------------------|-------------------------|
| 1     | Evento                 | Mantida                |
| 2     | FormulÃ¡rio de Lead     | Mantida                |
| 3     | GamificaÃ§Ã£o            | **SerÃ¡ substituÃ­da por Ingressos / Cotas** |
| 4     | **AtivaÃ§Ãµes**          | Aba atual              |
| 5     | QuestionÃ¡rio           | Em avaliaÃ§Ã£o           |

---

### 3.4 ConteÃºdo da Aba â€œAtivaÃ§Ãµesâ€

#### Ordem dos campos (lado esquerdo)

| #  | Campo                                 | Tipo                          | Mapeamento no Banco                         | ObservaÃ§Ã£o |
|----|---------------------------------------|-------------------------------|----------------------------------------------|------------|
| 1  | Nome da ativaÃ§Ã£o \*                   | Texto                         | `ativacao.nome`                              | ObrigatÃ³rio |
| 2  | Mensagem do QR Code                   | Textarea (mÃ¡x. 240 chars)     | `ativacao.mensagem_qrcode`                   | Exibida na tela do QR |
| 3  | Tipo de gamificaÃ§Ã£o                   | Dropdown                      | **NÃ£o persiste diretamente**                 | Categoria visual |
| 4  | Redirecionamento para tela de pesquisa| Switch booleano               | `ativacao.redireciona_pesquisa`              |            |
| 5  | Check-in Ãºnico por ativaÃ§Ã£o           | Switch booleano               | `ativacao.checkin_unico`                     | Define â€œÃšnico = Simâ€ |
| 6  | Termo de uso                          | Switch booleano               | `ativacao.termo_uso`                         |            |
| 7  | Gerar Cupom                           | Switch booleano               | `ativacao.gera_cupom`                        | Liga mÃ³dulo de cupons |
| 8  | BotÃ£o â€œAdicionar ativaÃ§Ã£oâ€            | AÃ§Ã£o                          | â€”                                            | Cria ativaÃ§Ã£o |

---

### 3.5 Lista de AtivaÃ§Ãµes (lado direito)

Colunas exibidas:

| Coluna         | DescriÃ§Ã£o |
|----------------|-----------|
| **Nome**       | Nome da ativaÃ§Ã£o cadastrada |
| **Ãšnico**      | â€œSimâ€ se `checkin_unico = TRUE` |
| **GamificaÃ§Ã£o**| â€œSimâ€ se qualquer switch de gamificaÃ§Ã£o estiver habilitado |
| **AÃ§Ãµes**      | Ver (azul), Editar (verde), Excluir (vermelho) |

---

## 4. Comportamento da Tela

### 4.1 Adicionar ativaÃ§Ã£o
- Valida campos obrigatÃ³rios  
- Cria registro em `ativacao`  
- Salva switches como booleans diretos  
- Caso sejam necessÃ¡rios textos de gamificaÃ§Ã£o (nome, descriÃ§Ã£o, prÃªmios), cria registro em `gamificacao` (1:1)  
- Atualiza tabela da direita

### 4.2 Editar ativaÃ§Ã£o
- BotÃ£o verde preenche novamente o formulÃ¡rio  
- AlteraÃ§Ãµes refletem direto no banco  
- Se switches forem desmarcados â†’ gamificaÃ§Ã£o pode ser removida

### 4.3 Excluir ativaÃ§Ã£o
- Remove ativaÃ§Ã£o  
- Remove gamificaÃ§Ã£o associada (ON DELETE CASCADE)  
- Pode exigir bloqueio caso existam leads conectados (regra futura)

### 4.4 LÃ³gica do campo â€œÃšnicoâ€
- Derivado exclusivamente de `checkin_unico`  
- Controla se um lead pode registrar apenas 1 interaÃ§Ã£o naquela ativaÃ§Ã£o

---

## 5. Regras de NegÃ³cio Principais

| Regra | Detalhe |
|-------|---------|
| Uma ativaÃ§Ã£o pertence a um Ãºnico evento | FK `evento_id` |
| AtivaÃ§Ã£o pode ter 0 ou mais mecÃ¢nicas de gamificaÃ§Ã£o | Representadas como switches |
| GamificaÃ§Ã£o detalhada existe em tabela separada | `gamificacao` (1:1 com ativacao) |
| Check-in Ãºnico | Impede mÃºltiplos registros por lead |
| Gerar Cupom | Integra com mÃ³dulo de cupons |
| Mensagem QR | Exibida na renderizaÃ§Ã£o do QR code da ativaÃ§Ã£o |

---

## 6. DiferenÃ§as â€“ Sistema Original Ã— Nova VersÃ£o

| Item                     | Sistema Original                 | Nova VersÃ£o                      |
|--------------------------|----------------------------------|----------------------------------|
| Switches de gamificaÃ§Ã£o | Independentes                    | Modelados como booleanos         |
| Tipo de gamificaÃ§Ã£o      | Dropdown pouco funcional         | Mantido apenas como referÃªncia   |
| Banco de dados           | Indefinido                       | Estrutura clara: ativaÃ§Ã£o + gamificaÃ§Ã£o 1:1 |
| QR Code                  | Parcialmente documentado         | Mapeado em `mensagem_qrcode`     |
| Cupons                   | Usado apenas em gamificaÃ§Ãµes     | Estrutura compatÃ­vel para expansÃ£o |

---

## 7. Modelo de Banco de Dados

### 7.1 Tabela `ativacao` (versÃ£o final)

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
